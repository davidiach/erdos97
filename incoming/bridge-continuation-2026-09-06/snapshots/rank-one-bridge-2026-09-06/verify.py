#!/usr/bin/env python3
"""Reproduce exact controls and deterministic finite regression reports.

Usage: python verify.py --write     (create verification.json)
       python verify.py --check     (compare to retained verification.json)
Only the Python standard library is required. The theorem is in proofs.md.
"""
from __future__ import annotations
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
import argparse
import json
import random

from checker import (Geometry, VerificationError, crosses, hull_indices,
                     minimum_layer_certificate, require, threshold_graph_certificate)
import fixtures

ROOT=Path(__file__).resolve().parent


def raw_fixture(geo, rho):
    return {'points':[[str(x),str(y)] for x,y in geo.points],
            'coordinate_encoding':'(x, sqrt(vertical_scale_squared)*y)',
            'vertical_scale_squared':str(geo.vertical_scale_squared),
            'cyclic_order':list(geo.order),
            'radii_squared':list(map(str,rho)),
            'closer_counts':list(geo.closer_counts(rho)),
            'selected_witnesses':[list(geo.witnesses(i,rho[i])) for i in range(len(rho))],
            'maximum_multiplicities':list(geo.maximum_multiplicities()),
            'supporting_line_checks':geo.support_count,
            'minimum_support_determinant_coefficient':str(geo.support_minimum)}


def controls():
    out={}
    for name,build in [('sharp_variable_minimum_layer',fixtures.sharp_variable),
                       ('two_short_pairs_at_one_center',fixtures.two_short_pairs),
                       ('rich_radius_larger_than_incident_side',fixtures.long_relative_to_side),
                       ('equilateral_triangle',fixtures.equilateral_triangle),
                       ('regular_hexagon',fixtures.regular_hexagon)]:
        geo,rho=build()
        out[name]={'geometry':raw_fixture(geo,rho),
                   'certificate':minimum_layer_certificate(geo,rho)}
    c=out['sharp_variable_minimum_layer']['certificate']
    require(c['minimum_layer']==[0,3,4], 'Sharp control minimum layer changed')
    require(c['rich_centers_in_minimum_layer']==[0], 'Sharp control rich center changed')
    require(c['graph']['face_budget']==1, 'Sharp face budget changed')
    require(out['sharp_variable_minimum_layer']['geometry']['selected_witnesses']
            ==[[1,2,3,4],[2],[1],[0],[0]], 'Realized-radius control changed')
    geo,rho=fixtures.long_relative_to_side()
    require(geo.d2[0][1]==F(101,10000), 'Short incident side changed')
    require(geo.witnesses(0,F(1))==(2,3,4,5), 'Long-radius rich row changed')
    require(geo.closer_counts(rho)[0]==1 and rho[0]==1,'Long-radius rank changed')
    for name,build in [('rank_two_pentagon',fixtures.rank_two_pentagon),
                       ('rank_two_eight',fixtures.rank_two_eight),
                       ('rank_two_square',fixtures.rank_two_square)]:
        geo,rho=build()
        data=raw_fixture(geo,rho)
        require(max(data['closer_counts'])==2, 'Rank-two control is not exactly rank two')
        try:
            minimum_layer_certificate(geo,rho)
        except VerificationError as exc:
            require(str(exc)=='One-closer-point hypothesis fails', 'Wrong rejection reason')
            data['rank_one_checker_rejection']=str(exc)
        else:
            raise VerificationError('Rank-two input was incorrectly accepted')
        data['minimum_layer']=[i for i,r in enumerate(rho) if r==min(rho)]
        out[name]=data
    require(out['rank_two_pentagon']['minimum_layer']==[0], 'Pentagon minimum layer changed')
    require(out['rank_two_pentagon']['selected_witnesses'][0]==[1,2,3,4], 'Pentagon star changed')
    e=out['rank_two_eight']
    require(e['radii_squared'][4]=='16/13', 'Eight-point higher radius changed')
    require(e['selected_witnesses'][0]==[1,2,3,4]
            and e['selected_witnesses'][4]==[2,5,6,7], 'Eight-point rich rows changed')
    require(e['closer_counts']==[0,1,2,2,2,2,2,2], 'Eight-point ranks changed')
    geo,rho=fixtures.rank_two_eight()
    require(geo.d2[3][4]<1 and rho[4]>rho[0], 'Strict propagation failure disappeared')
    expected=json.loads((ROOT/'rank_two_exact_control.json').read_text())
    require(e['points']==expected['points'], 'Independent formula does not match retained coordinates')
    require(e['radii_squared']==expected['radii_squared'], 'Retained radii do not match')
    # Rotation of the start of the hull is immaterial; compare edge sets.
    old=expected['cyclic_order'];new=e['cyclic_order']
    require({(old[i],old[(i+1)%8]) for i in range(8)}==
            {(new[i],new[(i+1)%8]) for i in range(8)}, 'Cyclic order mismatch')
    geo,rho=fixtures.rank_two_square()
    require(crosses(geo.points,(0,2),(1,3)), 'Square crossing disappeared')
    geo,rho=fixtures.three_witnesses_no_short_pair()
    w=geo.witnesses(0,F(1))
    require(len(w)==3 and all(geo.d2[a][b]>1 for a,b in combinations(w,2)),
            'Three-witness short-pair negative control failed')
    out['three_witnesses_no_short_pair']=raw_fixture(geo,rho)
    return out


@lru_cache(None)
def triangulations(labels: tuple[int,...]):
    if len(labels)<3:
        return ((),)
    ans=[]
    for k in range(1,len(labels)-1):
        t=(labels[0],labels[k],labels[-1])
        for a in triangulations(labels[:k+1]):
            for b in triangulations(labels[k:]):
                ans.append((t,)+a+b)
    return tuple(ans)


def all_matchings(n, edges):
    adjacent={i:[] for i in range(n)}
    for a,b in edges:
        adjacent[a].append(b);adjacent[b].append(a)
    def rec(remaining,chosen):
        if not remaining:
            yield tuple(chosen);return
        i=min(remaining);rest=remaining-{i}
        yield from rec(rest,chosen)
        for j in adjacent[i]:
            if j in rest:
                yield from rec(rest-{j},chosen+[(min(i,j),max(i,j))])
    yield from rec(set(range(n)),[])


def combinatorial_regression():
    rows=[]
    for n in range(3,9):
        ts=triangulations(tuple(range(n)))
        require(len(set(tuple(sorted(x)) for x in ts))==len(ts),'Repeated triangulation')
        matchings=0;max_coverage=0
        for faces in ts:
            require(len(faces)==n-2,'Wrong face count')
            edges=sorted({tuple(sorted(e)) for t in faces for e in combinations(t,2)})
            for red in all_matchings(n,edges):
                red=set(red);matchings+=1;apices=[]
                for t in faces:
                    bases=[tuple(sorted(e)) for e in combinations(t,2) if tuple(sorted(e)) in red]
                    require(len(bases)<=1,'Matching gave two short edges in a face')
                    if bases:
                        apices.append(next(i for i in t if i not in bases[0]))
                coverage=len(set(apices))
                require(coverage<=n-2,'Triangle-apex face budget exceeded')
                require(coverage<n,'Every vertex was covered')
                max_coverage=max(max_coverage,coverage)
        rows.append({'vertices':n,'triangulations':len(ts),'matchings':matchings,
                     'maximum_distinct_apices':max_coverage,'face_budget':n-2})
    return rows


def geometric_regression():
    rng=random.Random(97972026)
    geometries=[]
    # Actual integer hulls: coordinates are never rounded from floating point.
    for _ in range(36):
        pts=tuple(sorted({(F(rng.randrange(-20,21)),F(rng.randrange(-20,21)))
                          for _ in range(24)}))
        hull=hull_indices(pts)
        chosen=[pts[i] for i in hull[:8]]
        if len(chosen)>=3:
            geometries.append(Geometry.build(chosen))
    # Four-witness circles with a matching of strictly shorter witness chords.
    pool=[F(0),F(1,10),F(1,4),F(1,2),F(2,3),F(1),F(3,2),F(2),F(3),F(5),F(10)]
    stars=0
    for ts in combinations(pool,4):
        geo=Geometry.build([(F(0),F(0))]+[fixtures.unit(t) for t in ts])
        if max(geo.closer_counts([F(1)]*5))<=1:
            geometries.append(geo);stars+=1
    # Hereditary tests on every nonempty subset of the two-rich rank-two
    # control. Each subset is tested ONLY with its own rank-one radii.
    control,_=fixtures.rank_two_eight()
    subset_count=0
    for mask in range(1,1<<8):
        pts=[p for i,p in enumerate(control.points) if (mask>>i)&1]
        geometries.append(Geometry.build(pts));subset_count+=1
    for build in [fixtures.sharp_variable,fixtures.two_short_pairs,
                  fixtures.long_relative_to_side,fixtures.rank_two_pentagon,
                  fixtures.rank_two_square,fixtures.three_witnesses_no_short_pair,
                  fixtures.equilateral_triangle,fixtures.regular_hexagon]:
        geometries.append(build()[0])
    assignments=0;rich_assignments=0;rich_centers=0;support_checks=0
    common_scale_checks=0;quadrilateral_crossing_checks=0
    for geo in geometries:
        support_checks+=geo.support_count
        options=[geo.second_neighbor_options(i) for i in range(len(geo.points))]
        for rho in product(*options):
            cert=minimum_layer_certificate(geo,rho);assignments+=1
            k=len(cert['rich_centers_in_minimum_layer'])
            rich_centers+=k;rich_assignments+=bool(k)
        # Empty distance levels and strict intermediate radii are permitted.
        for _ in range(3):
            rho=[]
            for opts in options:
                if len(opts)==1:
                    rho.append(opts[0]/2 if rng.randrange(2) else opts[0])
                else:
                    rho.append((opts[0]+opts[-1])/2 if rng.randrange(2) else opts[0]/2)
            cert=minimum_layer_certificate(geo,rho);assignments+=1
            k=len(cert['rich_centers_in_minimum_layer'])
            rich_centers+=k;rich_assignments+=bool(k)
        # Common-scale planarity, separately from the minimum-layer routine.
        levels=sorted({geo.d2[a][b] for a,b in combinations(range(len(geo.points)),2)})
        for r2 in levels:
            if max(geo.closer_counts([r2]*len(geo.points)))<=1:
                threshold_graph_certificate(geo,tuple(range(len(geo.points))),r2)
                common_scale_checks+=1
        # Independent contrapositive of the noncrossing lemma, including
        # unequal crossing diagonals. A crossing at their larger scale must
        # exhibit a vertex with at least two strictly shorter connections.
        for ix in combinations(range(len(geo.order)),4):
            a,b,c,d=(geo.order[i] for i in ix)
            require(crosses(geo.points,(a,c),(b,d)),'Convex diagonals did not cross')
            r2=max(geo.d2[a][c],geo.d2[b][d])
            local=[sum(geo.d2[u][v]<r2 for v in (a,b,c,d) if u!=v) for u in (a,b,c,d)]
            require(max(local)>=2,'Crossing has a matching of all shorter edges')
            quadrilateral_crossing_checks+=1
    return {'geometric_fixtures':len(geometries),'integer_hull_fixtures':36,
            'matching_short_chord_stars':stars,'nonempty_eight_point_subsets':subset_count,
            'radius_assignments':assignments,'assignments_with_rich_minimum_layer':rich_assignments,
            'rich_minimum_layer_centers_checked':rich_centers,
            'supporting_line_checks':support_checks,'common_scale_planarity_checks':common_scale_checks,
            'crossing_quadrilateral_checks':quadrilateral_crossing_checks}


def report():
    return {'schema':1,'date':'2026-09-06',
            'status':'REVIEW_PENDING_RESTRICTED_PAPER_PROOF_WITH_EXACT_REGRESSION_CHECKS',
            'claim_scope':'Assigned radii with at most one strictly closer point at each center; arbitrary strictly convex finite sets.',
            'not_an_unrestricted_solution':True,'independent_external_review':False,
            'controls':controls(),'geometry_regression':geometric_regression(),
            'outerplanar_combinatorial_regression':combinatorial_regression()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write',action='store_true');mode.add_argument('--check',action='store_true')
    args=parser.parse_args()
    result=report();payload=json.dumps(result,indent=2,sort_keys=True)+'\n'
    path=ROOT/'verification.json'
    if args.write:
        path.write_text(payload)
    else:
        require(path.read_text()==payload,'Generated verification report does not match retained bytes')
    print(json.dumps({'passed':True,'mode':'write' if args.write else 'check',
                      'geometry':result['geometry_regression'],
                      'combinatorial':result['outerplanar_combinatorial_regression']},indent=2))

if __name__=='__main__':
    main()
