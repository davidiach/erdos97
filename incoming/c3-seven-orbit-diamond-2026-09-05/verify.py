#!/usr/bin/env python3
"""Reconstruct all integer models; optionally replay the full finite proof.

No solver or numerical package is imported. --full additionally requires a
C++17 compiler and checks every phase proof record, all 15^7 complete graphs,
and the separate expanded encodings. Geometry remains a written proof obligation.
"""
from __future__ import annotations
import argparse
from collections import Counter
import gzip
import hashlib
from itertools import permutations, product
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from algebra_controls import polynomial_checks, transitive_control
from common_supplier_background import controls, graph_well_formed
from core import AngleModel, MetricModel, all_cases, decode_case, require, verify_certificate
from graph_domain import generate, input_text, phase_count, contains_diamond, target_graph
ROOT = Path(__file__).resolve().parent
DIAMOND = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)]
EXPECTED_PHASE = {'graphs': 177, 'cases': 7718400, 'crossing': 5754240, 'kalmanson_zero': 0, 'kalmanson_inverse': 1963930, 'angle_residuals': 230, 'exhausted_supplied_domain': True, 'elementary_replay_passed': True}

def load(name: str):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def case_key(record: dict) -> tuple:
    return (tuple(record['rows']), tuple(record['order']), tuple(record['gains']))

def diamond_arrows(record: dict) -> list[tuple[int, int, int]]:
    order, shifts = (record['order'], record['shifts'])
    require(len(order) == 4 and order[0] == 0 and (sorted(order) == list(range(4))), 'bad diamond order')
    require(len(shifts) == 4 and shifts[0] == 0 and all((type(x) is int and x in range(3) for x in shifts)), 'bad diamond representative shifts')
    pos = {v: i for i, v in enumerate(order)}
    return [(pos[a], pos[b], (shifts[b] - shifts[a]) % 3) for a, b in DIAMOND]

def seven_model_input(record: dict) -> tuple[list, list]:
    rows, order, gains = (record['rows'], record['order'], record['gains'])
    require(len(rows) == 7 and graph_well_formed(rows), 'bad seven-orbit graph')
    require(len(order) == 7 and order[0] == 0 and (sorted(order) == list(range(7))), 'bad seven-orbit order')
    require(len(gains) == 14 and all((type(g) is int and g in range(3) for g in gains)), 'bad seven-orbit gains')
    pos = {v: i for i, v in enumerate(order)}
    edges = [(i, j) for i in range(7) for j in range(7) if rows[i] >> j & 1]
    for (a, b), gain in zip(edges, gains):
        allowed = (0, 2 if pos[b] > pos[a] else 1) if a < b else (1 if pos[b] > pos[a] else 2,)
        require(gain in allowed, 'gain violates source-target radius direction')
    return ([(pos[a], pos[b], g) for (a, b), g in zip(edges, gains)], [(pos[max(a, b)], pos[min(a, b)]) for a, b in edges])

def certificate_summary(records: list[dict]) -> dict:
    return {'cases': len(records), 'max_nonzero_terms': max((len(r['positive']) + len(r['equality']) for r in records)), 'max_abs_multiplier': max((abs(w) for r in records for _, w in r['positive'] + r['equality']))}

def verify_common() -> dict:
    blob = load('common_supplier_certificates.json')
    require(blob['schema'] == 'erdos97.c3_common_supplier_certificates.v1', 'bad common-supplier schema')
    records = blob['records']
    seen = set()
    census = Counter()
    models = [AngleModel(4), MetricModel(4)]
    for record in records:
        require(len(record) == 6, 'bad common-supplier record')
        topology, code, mode, kind, positive, equality = record
        key = (topology, code, mode)
        require(key not in seen and kind in (0, 1), 'duplicate case or unknown model')
        seen.add(key)
        arrows, greater = decode_case(key)
        A, E = models[kind].build(arrows, greater)
        verify_certificate(A, E, positive, equality)
        census[kind] += 1
    require(seen == set(all_cases()) and len(records) == 486, 'incomplete common-supplier coverage')
    require(census == {0: 480, 1: 6}, 'common-supplier census mismatch')
    return {'angle_certificates': 480, 'ordinary_distance_certificates': 6, 'exact_coverage': True}

def transitive_model_input(record: dict) -> tuple[list, list]:
    order, shifts = (record['order'], record['shifts'])
    require(len(order) == 3 and order[0] == 0 and (sorted(order) == [0, 1, 2]), 'bad transitive order')
    require(len(shifts) == 3 and shifts[0] == 0 and all((type(s) is int and s in range(3) for s in shifts)), 'bad transitive shifts')
    pos = {v: i for i, v in enumerate(order)}
    arrows = [(pos[a], pos[b], (shifts[b] - shifts[a]) % 3) for a, b in [(0, 1), (0, 2), (1, 2)]]
    return (arrows, [(pos[1], pos[2]), (pos[2], pos[0])])

def verify_transitive_radius() -> dict:
    records = load('transitive_radius_certificates.json')
    expected = {(tuple([0, *tail]), tuple([0, *shifts])) for tail in permutations([1, 2]) for shifts in product(range(3), repeat=2)}
    model = AngleModel(3)
    seen = set()
    for r in records:
        key = (tuple(r['order']), tuple(r['shifts']))
        require(key not in seen and r['kind'] == 0, 'duplicate/invalid transitive case')
        seen.add(key)
        A, E = model.build(*transitive_model_input(r))
        verify_certificate(A, E, r['positive'], r['equality'])
    require(seen == expected and len(records) == 18, 'transitive radius coverage mismatch')
    return {**certificate_summary(records), 'exact_coverage': True, 'forbidden_order': 'r_A < r_C < r_B', 'conclusion_with_elementary_reduction': 'r_B < r_A < r_C'}

def verify_diamond(records: list[dict] | None=None) -> dict:
    records = load('diamond_certificates.json') if records is None else records
    expected = {(tuple([0, *tail]), (0, *shift)) for tail in permutations([1, 2, 3]) for shift in product(range(3), repeat=3)}
    seen = set()
    model = AngleModel(4)
    for r in records:
        key = (tuple(r['order']), tuple(r['shifts']))
        require(key not in seen and r['kind'] == 0, 'duplicate/invalid diamond case')
        seen.add(key)
        A, E = model.build(diamond_arrows(r), [])
        verify_certificate(A, E, r['positive'], r['equality'])
    require(seen == expected and len(records) == 162, 'incomplete diamond coverage')
    return {**certificate_summary(records), 'exact_coverage': True, 'radius_comparisons_used': False}

def verify_seven(graphs: list[list[int]]) -> dict:
    records = load('seven_angle_certificates.json')
    seen = set()
    allowed = {tuple(g) for g in graphs}
    model = AngleModel(7)
    for r in records:
        key = case_key(r)
        require(key not in seen and tuple(r['rows']) in allowed and (r['kind'] == 0), 'invalid/duplicate residual')
        seen.add(key)
        arrows, greater = seven_model_input(r)
        A, E = model.build(arrows, greater)
        verify_certificate(A, E, r['positive'], r['equality'])
    require(len(records) == 230, 'wrong residual certificate count')
    return {**certificate_summary(records), 'exact_residual_identities': True, 'phase_coverage_checked_only_by_full_replay': True}

def expanded_audit() -> dict:
    from audit_expanded_model import ExpandedEncoding
    e4, e7 = (ExpandedEncoding(4), ExpandedEncoding(7))
    e3, a3 = (ExpandedEncoding(3), AngleModel(3))
    for r in load('transitive_radius_certificates.json'):
        arrows, greater = transitive_model_input(r)
        require(e3.angles(arrows, greater) == a3.build(arrows, greater), 'expanded transitive radius mismatch')
    a4, a7 = (AngleModel(4), AngleModel(7))
    common_records = load('common_supplier_certificates.json')['records']
    m4 = MetricModel(4)
    for topology, code, mode, kind, _, _ in common_records:
        arrows, greater = decode_case((topology, code, mode))
        if kind == 0:
            require(e4.angles(arrows, greater) == a4.build(arrows, greater), 'expanded common angle mismatch')
        else:
            require(e4.metric(arrows, greater) == m4.build(arrows, greater), 'expanded common distance mismatch')
    for r in load('diamond_certificates.json'):
        arrows = diamond_arrows(r)
        require(e4.angles(arrows, []) == a4.build(arrows, []), 'expanded diamond mismatch')
    for r in load('seven_angle_certificates.json'):
        arrows, greater = seven_model_input(r)
        require(e7.angles(arrows, greater) == a7.build(arrows, greater), 'expanded seven-orbit mismatch')
    return {'common_cases': 486, 'transitive_radius_cases': 18, 'diamond_cases': 162, 'seven_residuals': 230, 'expanded_seven_chords': 210, 'folded_seven_chord_classes': 70, 'encoding_mismatches': 0}

def static_report() -> dict:
    graphs, statistics = generate(7)
    require(graphs == load('radial_graphs.json'), 'stored radial graph list mismatch')
    require((ROOT / 'radial_graphs.txt').read_text() == input_text(graphs), 'graph text/JSON mismatch')
    require([statistics[k] for k in ['after_radial_path', 'after_common_supplier', 'after_diamond', 'after_transitive_radius_order']] == [2755, 1027, 349, 177], 'graph census mismatch')
    require(phase_count(graphs) == EXPECTED_PHASE['cases'], 'phase domain size mismatch')
    lower = []
    for m in range(3, 7):
        survivors, counters = generate(m)
        require(not survivors, f'unexpected smaller survivor at m={m}')
        lower.append(counters)
    target = target_graph()
    witness = contains_diamond(target)
    require(witness is not None, 'previous seven-orbit guardrail not caught')
    return {'schema': 'erdos97.c3_diamond_seven.v1', 'status': 'REVIEW_PENDING_COMPUTER_ASSISTED_RESTRICTED_THEOREM', 'scope': 'Own-triangle-side C3 systems only; not unrestricted Erdos97, not an accepted general finite bound.', 'common_supplier_background': verify_common(), 'transitive_radius_rule': verify_transitive_radius(), 'diamond': verify_diamond(), 'seven_angle_certificates': verify_seven(graphs), 'radial_domain': statistics, 'smaller_domains': lower, 'phase_domain_cases': phase_count(graphs), 'previous_guardrail_diamond': list(witness), 'polynomial_identities': polynomial_checks(), 'transitive_triangle_is_permitted': transitive_control(), 'other_positive_controls': controls(), 'proof_stream': {'compressed_sha256': sha(ROOT / 'phase_certificates.bin.gz'), 'compressed_bytes': (ROOT / 'phase_certificates.bin.gz').stat().st_size, 'uncompressed_expected_bytes': 8 + 5 * phase_count(graphs)}, 'elementary_records_checked_by_this_static_report': False, 'repository_wide_CI_run': False}

def compiled_checks(regenerate: bool=False, sanitize: bool=False) -> dict:
    compiler = shutil.which(os.environ.get('CXX', 'c++'))
    require(compiler is not None, 'C++17 compiler required for full replay')
    compiler_version = subprocess.run([compiler, '--version'], check=True, text=True, capture_output=True).stdout.splitlines()[0]
    graphs = load('radial_graphs.json')
    records = load('seven_angle_certificates.json')
    expected_keys = {case_key(r) for r in records}
    with tempfile.TemporaryDirectory(prefix='erdos97-seven-') as directory:
        tmp = Path(directory)
        proof = tmp / 'phase.bin'
        with gzip.open(ROOT / 'phase_certificates.bin.gz', 'rb') as src, proof.open('wb') as out:
            shutil.copyfileobj(src, out)
        require(proof.stat().st_size == 8 + 5 * phase_count(graphs), 'bad proof stream length')

        def compile_source(name):
            target = tmp / name
            flags = ['-O3', '-std=c++17', '-Wall', '-Wextra', '-Wpedantic']
            if sanitize:
                flags = ['-O1', '-g', '-std=c++17', '-fsanitize=undefined', '-fno-sanitize-recover=undefined']
            result = subprocess.run([compiler, *flags, str(ROOT / f'{name}.cpp'), '-o', str(target)], check=True, text=True, capture_output=True, timeout=180)
            require(not result.stderr, 'unexpected compiler diagnostic: ' + result.stderr)
            return target
        binary = compile_source('phase_replay')
        result = subprocess.run([str(binary), str(proof)], input=input_text(graphs), check=True, text=True, capture_output=True, timeout=1200)
        replay = [json.loads(s) for s in result.stdout.splitlines()]
        require(len(replay) == 230 and {case_key(r) for r in replay} == expected_keys, 'phase-to-angle coverage mismatch')
        stats = json.loads(result.stderr)
        require(stats == EXPECTED_PHASE, 'elementary proof census mismatch')
        oracle = compile_source('graph_oracle')
        output = subprocess.run([str(oracle)], check=True, text=True, capture_output=True, timeout=1200)
        require(not output.stderr, 'graph oracle diagnostic')
        domain = json.loads(output.stdout)
        require(domain['graphs'] == graphs and domain['complete_tuples'] == 15 ** 7 and domain['exhausted'], 'complete product domain mismatch')
        stored = load('graph_oracle_report.json')
        require(domain == stored, 'stored graph oracle report mismatch')
        if regenerate:
            search = compile_source('phase_search')
            fresh = tmp / 'fresh.bin'
            output = subprocess.run([str(search), str(fresh)], input=input_text(graphs), check=True, text=True, capture_output=True, timeout=1200)
            require(sha(fresh) == sha(proof), 'regenerated phase proof differs')
            found = [json.loads(s) for s in output.stdout.splitlines()]
            for r in found:
                r['rows'] = graphs[r['graph']]
            require(len(found) == 230 and {case_key(r) for r in found} == expected_keys, 'regenerated residual mismatch')
        return {'compiler': compiler_version, 'elementary_phase_replay': stats, 'proof_uncompressed_sha256': sha(proof), 'full_graph_product': {k: v for k, v in domain.items() if k != 'graphs'}, 'residual_certificate_coverage_exact': True, 'fresh_phase_regeneration': regenerate, 'undefined_behavior_sanitization': sanitize}

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='regenerate static report.json')
    parser.add_argument('--check', action='store_true', help='compare static report.json')
    parser.add_argument('--full', action='store_true', help='replay every phase, all complete graph tuples, and expanded models')
    parser.add_argument('--regenerate-phase', action='store_true', help='also rediscover all elementary certificates and compare bytes')
    parser.add_argument('--sanitize', action='store_true', help='use undefined-behavior sanitizer for compiled checks')
    parser.add_argument('--output', type=Path, help='save actual validation result for this invocation')
    args = parser.parse_args()
    require(not (args.write and args.check), 'choose --write or --check, not both')
    report = static_report()
    if args.write:
        (ROOT / 'report.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    if args.check:
        require(report == load('report.json'), 'stored static report mismatch')
    result = {'static_checks': 'passed', 'static_report_sha256': sha(ROOT / 'report.json') if (ROOT / 'report.json').exists() else None, 'full_proof_replayed': False, 'scope': report['scope']}
    if args.full or args.regenerate_phase or args.sanitize:
        result['compiled'] = compiled_checks(args.regenerate_phase, args.sanitize)
        result['expanded_encodings'] = expanded_audit()
        result['full_proof_replayed'] = True
    result['status'] = 'all requested checks passed'
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(text)
    print(text, end='')
if __name__ == '__main__':
    main()
