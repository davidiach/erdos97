"""
Run Gröbner basis on all 15 n=8 patterns.
"""
import json
import time
import signal
from sympy import symbols, groebner, QQ, S
from sympy.polys.orderings import grevlex


def build_system(witnesses, n):
    xs = [symbols(f'x{i}') for i in range(n)]
    ys = [symbols(f'y{i}') for i in range(n)]
    eqs = []
    for i, w in enumerate(witnesses):
        d2 = []
        for j in w:
            d2.append((xs[i] - xs[j])**2 + (ys[i] - ys[j])**2)
        eqs.append(d2[0] - d2[1])
        eqs.append(d2[0] - d2[2])
        eqs.append(d2[0] - d2[3])
    subs = {xs[0]: S.Zero, ys[0]: S.Zero, ys[1]: S.Zero, xs[1]: S.One}
    eqs = [e.subs(subs).expand() for e in eqs]
    eqs = [e for e in eqs if e != 0]
    free = []
    for i in range(n):
        for v in [xs[i], ys[i]]:
            if v not in subs:
                free.append(v)
    return free, eqs


def with_timeout(fn, timeout_sec):
    def handler(signum, frame):
        raise TimeoutError()
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(int(timeout_sec))
    try:
        result = fn()
        signal.alarm(0)
        return result
    except TimeoutError:
        signal.alarm(0)
        return 'TIMEOUT'
    except Exception as ex:
        signal.alarm(0)
        return f'ERROR: {ex}'


def main():
    with open('/home/user/erdos97/data/incidence/n8_reconstructed_15_survivors.json') as f:
        patterns = json.load(f)
    n = 8
    results = []
    for pat in patterns:
        pid = pat['id']
        rows = pat['rows']
        witnesses = [tuple(j for j, v in enumerate(row) if v == 1) for row in rows]
        free, eqs = build_system(witnesses, n)
        t0 = time.time()
        gb = with_timeout(lambda: groebner(eqs, *free, order='grevlex', domain=QQ), 120)
        elapsed = time.time() - t0
        if isinstance(gb, str):
            verdict = gb
            ngb = -1
        else:
            polys = list(gb)
            ngb = len(polys)
            if len(polys) == 1 and polys[0] == 1:
                verdict = 'UNREALIZABLE (GB={1})'
            else:
                verdict = f'NONTRIVIAL: {len(polys)} polys'
        print(f'Pattern {pid:2d}: vars={len(free)}, eqs={len(eqs)}, time={elapsed:7.2f}s, gb_size={ngb}, {verdict}')
        results.append((pid, elapsed, ngb, verdict))

    print()
    print('Summary:')
    killed = sum(1 for _, _, _, v in results if v.startswith('UNREALIZABLE'))
    nontrivial = sum(1 for _, _, _, v in results if v.startswith('NONTRIVIAL'))
    timed_out = sum(1 for _, _, _, v in results if v == 'TIMEOUT')
    errors = sum(1 for _, _, _, v in results if v.startswith('ERROR'))
    print(f'  Killed: {killed}/15')
    print(f'  Nontrivial: {nontrivial}/15')
    print(f'  Timed out: {timed_out}/15')
    print(f'  Errors: {errors}/15')


if __name__ == '__main__':
    main()
