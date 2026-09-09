"""Regenerate and compare every exact result; --write regenerates the report."""
import argparse
from core import ROOT, run, canonical

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = run()
    payload = canonical(report)
    path = ROOT / 'data/verification.json'
    if args.write:
        path.write_text(payload)
    elif path.read_text() != payload:
        raise AssertionError('stored exact report differs from fresh replay')
    print('84 old triples replayed; 42 slots; 1722 directed interval pairs; 123 possible edges.')
    print('Peeling layer sizes:', [len(x) for x in report['peeling_layers']])
    print('Core:', report['remaining_core'])
    print('Unique cap extension maxima:', report['core_classification']['maxima'])
    print('Positive control:', report['positive_control']['selected_slots'])

if __name__ == '__main__':
    main()
