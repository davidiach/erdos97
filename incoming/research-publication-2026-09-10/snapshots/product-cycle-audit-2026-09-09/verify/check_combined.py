"""Replay stored exact rejections: base chord-angle or diamond phase certificates."""
from pathlib import Path
import json,sys,argparse
from check_c3 import Geometry
from diamond_phase import check

def verify(data):
    if sys.flags.optimize:raise ValueError('assertions disabled')
    cases=data['cases'];seen=set();angle=phase=terms=0
    for c in cases:
        key=json.dumps(c['rows'])
        if key in seen:raise ValueError('duplicate system')
        seen.add(key);g=Geometry(c['rows'])
        if c.get('certificate')is not None:
            g.certificate(c['certificate']);angle+=1;terms+=sum(map(len,c['certificate'].values()))
        elif c.get('diamond_phase_certificate')is not None:
            check(c['rows'],c['diamond_phase_certificate']);phase+=1;terms+=sum(map(len,c['diamond_phase_certificate'].values()))
        else:raise ValueError('uncertified case')
    return {'status':'PASS_ALL_STORED_FIXED_SYSTEM_CERTIFICATES','unique_cases':len(cases),'base_angle_certificates':angle,'diamond_phase_certificates':phase,'integer_terms':terms,
      'all_nine_orbit_patterns_exhausted':False,'unrestricted_solution':False,'external_review':False}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('--output');a=ap.parse_args();r=verify(json.loads(Path(a.input).read_text()));text=json.dumps(r,indent=2)+'\n'
    if a.output:Path(a.output).write_text(text)
    print(text)
