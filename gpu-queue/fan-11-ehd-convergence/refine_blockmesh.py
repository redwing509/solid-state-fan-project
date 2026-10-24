#!/usr/bin/env python3
"""Uniformly refine the in-plane cell counts of every hex block in a blockMeshDict by integer factor R.
z count (1, 2-D case) is left unchanged; simpleGrading ratios are preserved, so the refinement is uniform."""
import re, sys
path, R = sys.argv[1], int(sys.argv[2])
s = open(path).read()
pat = re.compile(r'(hex\s*\([\d\s]+\)\s*)\((\d+)\s+(\d+)\s+(\d+)\)')
n = 0
def f(m):
    global n; n += 1
    return '%s(%d %d %s)' % (m.group(1), int(m.group(2)) * R, int(m.group(3)) * R, m.group(4))
s2 = pat.sub(f, s)
assert n == 10, "expected 10 hex blocks, found %d" % n
open(path, 'w').write(s2)
print("refined %d blocks by %d" % (n, R))
