"""Retain and independently check all final metric cancellation branches."""
from pathlib import Path
from unittest.mock import patch
import argparse
import hashlib
import json

import geometry as G
import row_search
from certificate_arithmetic import check

ROOT=Path(__file__).resolve().parent


def run():
    endings=json.loads((ROOT/'exploratory/final_leaf_checks.json').read_text())
    cases=[];all_records=[]
    for ending in endings:
        cells,old=ending['cells'],ending['olds']
        triangles=[G.context()[4][i]for i in cells]
        for coordinate,edge,child in ending['path']:
            triangles[coordinate]=G.split(triangles[coordinate],edge)[child]
        retained=[];node_count=0
        original=row_search.obstruction
        def record(rows,ranks,old_count=9):
            proof=original(rows,ranks,old_count)
            if proof is not None:
                entry=dict(rows=rows,**proof)
                check(entry,ranks)
                retained.append(entry)
            return proof
        with patch.object(row_search,'obstruction',record):
            for model in G.models(*triangles,cells,old):
                result=row_search.Search(model).run()
                if result['status']!='exhausted':raise ValueError('Final leaf remains open')
                node_count+=result['nodes']
        all_records.extend(retained)
        cases.append(dict(cells=cells,old_witnesses=old,path=ending['path'],
                          row_search_nodes=node_count,cancellations=retained))
    unique={json.dumps(r['rows'],sort_keys=True)for r in all_records}
    return dict(status='passed',cases=cases,terminal_cancellations=len(all_records),
                distinct_closed_witness_systems=len(unique),
                zero=sum(r['type']=='zero'for r in all_records),
                inverse=sum(r['type']=='inverse'for r in all_records),
                arithmetic_checker='certificate_arithmetic.py')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--check',action='store_true');args=ap.parse_args()
    text=json.dumps(run(),sort_keys=True,indent=2)+'\n';path=ROOT/'data/last_leaf_cancellations.json'
    if args.write:path.write_text(text)
    if args.check and path.read_text()!=text:raise ValueError('Final cancellation archive differs')
    print(text)
