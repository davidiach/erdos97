#!/usr/bin/env python3
"""Deterministic exact regression and control verifier.

Run --write to regenerate verification.json and exact_controls.json.
Run --check to compare regenerated objects with the stored objects.
The finite census is not an exhaustive classification of real polygons.
"""
from __future__ import annotations
import argparse
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations, product
import json
from pathlib import Path
import random

from geometry import Geometry, contains_disk, determinant, jsonable, require, unit
from combinatorial import audit as ear_audit
from fixtures import (all_controls, double_star, five_point_escape,
                      nine_point_return, third_nearest_squared)

ROOT = Path(__file__).resolve().parent


def hull(points):
    pts = sorted(set(points)); answer=[]
    for seq in (pts,pts[::-1]):
        chain=[]
        for p in seq:
            while len(chain)>=2 and determinant(chain[-2],chain[-1],p)<=0:
                chain.pop()
            chain.append(p)
        answer.extend(chain[:-1])
    return answer


def control_reports():
    reports=[]
    for item in all_controls():
        g=Geometry(item['points'],item.get('vertical_scale_squared',1))
        out={**item,'cyclic_order':g.order,'supporting_line_checks':g.support_count,
             'minimum_support_coefficient':g.minimum_support,
             'all_radius_maximum_multiplicities':g.multiplicities()}
        if 'thresholds_squared' in item:
            out['threshold_certificates']=[g.threshold(r) for r in item['thresholds_squared']]
        if 'radii_squared' in item:
            radii=item['radii_squared']; out['assigned_rows']=g.rows(radii)
            out['mutual_short_certificate']=g.mutual_short(radii)
            out['minimum_layer_certificate']=g.layer_escape(radii)
            require([Q(x) for x in radii]==third_nearest_squared(g),
                    'A control radius is not its actual third-nearest distance.')
        if item['name']=='nine_point_rational_return':
            require(g.multiplicities()==[4,1,1,1,1,4,1,1,1], 'Wrong full return profile.')
            require(g.order==[7,5,4,0,1,2,3,6,8], 'Wrong return hull order.')
            require(g.minimum_support==Q(209808,25628605),'Wrong exact supporting margin.')
            rows=g.rows(item['radii_squared'])
            require(rows['witnesses'][0]==[1,2,3,4], 'Wrong minimum witness row.')
            require(rows['witnesses'][5]==[0,6,7,8], 'Wrong return witness row.')
            require(rows['closer'][5]==[3,4], 'Wrong return closer row.')
            sub=Geometry(g.points[1:]); after=sub.multiplicities()
            require(after==[1,1,1,1,3,1,1,1], 'Deletion did not remove the rich class.')
            out['delete_minimum_layer']={'deleted_labels':[0],
                'remaining_original_labels':list(range(1,9)),
                'all_radius_maximum_multiplicities':after,
                'return_center_maximum_before':4,'return_center_maximum_after':3}
        reports.append(out)
    f=five_point_escape(); g=Geometry(f['points'])
    # The disk centered at point 1 of radius 2 contains the unit disk at 0.
    require(contains_disk(4,1,g.d2[0][1]),'Tangency containment failed.')
    closer=[j for j in range(g.n) if j!=1 and g.d2[1][j]<4]
    require(len(closer)==4,'The containment lower bound is not attained.')
    reports.append({'name':'disk_containment_four_closer_equality',
        'base_fixture':f['name'],'rich_center':0,'contained_radius_squared':1,
        'container_center':1,'container_radius_squared':4,
        'strictly_closer_vertices_at_container':closer,
        'note':'Exactly four closer points: this is outside the at-most-three hypothesis.'})
    return reports


def sample_geometries():
    # Deterministic selected subsets; these are bounded test domains only.
    parameters=[Q(-4),Q(-2),Q(-1),Q(-1,2),Q(0),Q(1,3),Q(1),Q(2),Q(5)]
    circle=[unit(t) for t in parameters]
    for size in range(3,8):
        for ids in combinations(range(9),size):
            if sum((i+1)*j for i,j in enumerate(ids))%5:
                continue
            yield 'circle_subset',Geometry([circle[i] for i in ids])
            yield 'ellipse_subset',Geometry([(3*circle[i][0],circle[i][1]) for i in ids])
    graph=[(Q(i),Q(i*i)) for i in range(-4,5)]
    for size in range(3,8):
        for ids in combinations(range(9),size):
            if sum(ids)%5==0:
                yield 'parabola_subset',Geometry([graph[i] for i in ids])
    rng=random.Random(970206)
    for _ in range(240):
        pts=hull([(Q(rng.randrange(-50,51)),Q(rng.randrange(-50,51))) for _ in range(18)])
        if len(pts)>=4:
            yield 'integer_hull',Geometry(pts)
    for first,second,third,fourth in product(
            (0,Q(1,10),Q(1,7)), (Q(1,3),Q(1,2),Q(2,3)),
            (Q(2),Q(3),Q(4)), (Q(7),Q(10),Q(15))):
        yield 'five_point_star',Geometry([(Q(0),Q(0))]+[unit(t) for t in (first,second,third,fourth)])
    for a,b,c in product((Q(2,3),Q(3,4),Q(4,5)),(Q(5,2),Q(3),Q(7,2)),(10,15,20,25)):
        pts=double_star(a,b,c)
        if len(hull(pts))==len(pts):
            yield 'double_star',Geometry(pts)
    for item in all_controls():
        yield 'named_control',Geometry(item['points'],item.get('vertical_scale_squared',1))


def regression_report():
    counts=Counter(); by_family=Counter(); applicable_by_family=Counter()
    examples=[]; rng=random.Random(970207)
    for family,g in sample_geometries():
        counts['geometries']+=1; by_family[family]+=1
        counts['supporting_line_checks']+=g.support_count
        counts['convex_quadrilaterals']+=g.crossing_diagonal_lemma()['quadrilaterals']
        distances=sorted({g.d2[i][j] for i,j in combinations(range(g.n),2)})
        thresholds=[Q(1)] if not distances else [distances[0]/2]
        for k,d in enumerate(distances):
            # Eligibility is checked directly before invoking the theorem checker.
            if max(sum(g.d2[i][j]<d for j in range(g.n) if j!=i) for i in range(g.n))>2:
                break
            thresholds.append(d)
            after=(d+distances[k+1])/2 if k+1<len(distances) else d+1
            if max(sum(g.d2[i][j]<after for j in range(g.n) if j!=i) for i in range(g.n))<=2:
                thresholds.append(after)
        for r in thresholds:
            cert=g.threshold(r); counts['fixed_radius_checks']+=1
            counts['fixed_radius_unit_edges_counted']+=cert['unit_edge_count']
            counts['non_gabriel_unit_edges_checked']+=len(cert['non_gabriel_unit_blockers'])
            counts['short_cycle_components_checked']+=cert['short_cycles']
            counts['cycle_ear_charges_checked']+=len(cert['cycle_ear_charges'])
        if g.n<4:
            continue
        candidates=[]
        for i in range(g.n):
            row=sorted(g.d2[i][j] for j in range(g.n) if j!=i)
            values={row[0], row[1], row[2], row[0]/2}
            if row[1]<row[2]:
                values.add((row[1]+row[2])/2)
            candidates.append(sorted(values))
        assignments=[third_nearest_squared(g)]
        assignments += [[v[0] for v in candidates],[v[-1] for v in candidates]]
        assignments += [[rng.choice(v) for v in candidates] for _ in range(9)]
        assignments=[list(v) for v in dict.fromkeys(tuple(a) for a in assignments)]
        for radii in assignments:
            g.mutual_short(radii); counts['variable_radius_assignments']+=1
            cert=g.layer_escape(radii)
            if cert['all_minimum_vertices_rich']:
                counts['all_rich_minimum_layer_checks']+=1; applicable_by_family[family]+=1
                counts['exported_incidences_checked']+=cert['export_count']
                if len(cert['minimum_layer'])>=2:
                    counts['multiple_minimum_center_checks']+=1
                # Bound and noncontainment for every selected edge into a higher radius.
                rows=g.rows(radii)
                for i in range(g.n):
                    if len(rows['witnesses'][i])<4:
                        continue
                    for j in rows['witnesses'][i]:
                        if radii[j]>radii[i]:
                            require(radii[j]<4*radii[i], 'Ascent radius band failed.')
                            counts['ascending_selected_edges_checked']+=1
                if len(examples)<3:
                    examples.append({'family':family,'points':g.points,
                                     'radii_squared':radii,'minimum_layer':cert['minimum_layer']})
    require(counts['all_rich_minimum_layer_checks']>0,'No positive layer controls exercised.')
    require(counts['multiple_minimum_center_checks']>0,'No multi-center layer controls exercised.')
    require(counts['cycle_ear_charges_checked']>0,'No nontriangular cycle charge exercised.')
    require(counts['non_gabriel_unit_edges_checked']>0,'No non-Gabriel unit edge exercised.')
    return {'counts':dict(sorted(counts.items())), 'geometries_by_family':dict(sorted(by_family.items())),
            'applicable_layer_checks_by_family':dict(sorted(applicable_by_family.items())),
            'first_positive_examples':examples}


def generate():
    controls=control_reports()
    report={'schema':1,'status':'REVIEW_PENDING_RESTRICTED_PAPER_PROOFS_WITH_EXACT_REGRESSION',
            'date':'2026-09-06',
            'scope':'At most two strictly closer vertices; fixed-radius edge bound and minimum-layer escape. No all-rich rank-two impossibility or unrestricted solution.',
            'arithmetic':'Python standard-library Fraction; coordinate floats rejected',
            'regression':regression_report(),
            'finite_ear_resource_audit':ear_audit(9),
            'named_controls':len(controls),
            'new_return_control':next(x for x in controls if x['name']=='nine_point_rational_return'),
            'limitations':['Finite regression does not quantify over all real polygons.',
                'The paper geometric and graph arguments require independent mathematical review.',
                'The nine-point control is not globally four-rich.',
                'No repository-wide tests, published novelty, or independent implementation review is claimed.']}
    return jsonable(report),jsonable(controls)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write',action='store_true'); mode.add_argument('--check',action='store_true')
    args=parser.parse_args(); report,controls=generate()
    outputs={'verification.json':report,'exact_controls.json':controls,
             'return_control.json':report['new_return_control']}
    for name,data in outputs.items():
        path=ROOT/name
        if args.write:
            path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
        else:
            require(path.exists(),f'Missing {name}; run --write.')
            require(json.loads(path.read_text())==data,f'Regenerated object differs: {name}.')
    print(json.dumps({'result':'PASS','mode':'write' if args.write else 'check',
                      'counts':report['regression']['counts']},indent=2))

if __name__=='__main__':
    main()
