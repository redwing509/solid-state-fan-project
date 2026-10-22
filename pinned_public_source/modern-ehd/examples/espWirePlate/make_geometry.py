#!/usr/bin/env python3
# Generate a one-wire wire-duct ESP case from the espWirePlate template
# with different wire radius / duct height / length.
# usage: make_geometry.py <newCaseDir> <rw> <H> <halfLength>
# e.g. the experimental geometry of Ziedan et al. (2010), Fig. 9:
#      make_geometry.py esp935 0.000935 0.2 0.4

import math
import os
import shutil
import sys

TEMPLATE = os.path.dirname(os.path.abspath(__file__))

case, rw, H, L = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
s = 0.02            # O-grid square half-size
z = 0.01            # slab thickness
c = rw/math.sqrt(2.0)
nV = max(30, int(round(30*(H - s)/0.0943)))   # vertical cells scale with height
nL = max(40, int(round(40*(L - s)/0.2086)))   # horizontal cells scale with length

if os.path.exists(case):
    shutil.rmtree(case)
os.makedirs(case)
for d in ("0", "constant", "system"):
    shutil.copytree(os.path.join(TEMPLATE, d), os.path.join(case, d))

bm = f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}

scale   1;

vertices
(
    (-{L}     0           0)
    (-{s}       0           0)
    (-{rw}      0           0)
    ( {rw}      0           0)
    ( {s}       0           0)
    ( {L}     0           0)
    (-{c:.8f} {c:.8f}  0)
    ( 0          {rw}       0)
    ( {c:.8f} {c:.8f}  0)
    (-{s}       {s}        0)
    ( 0          {s}        0)
    ( {s}       {s}        0)
    (-{L}     {s}        0)
    ( {L}     {s}        0)
    (-{L}     {H}      0)
    (-{s}       {H}      0)
    ( 0          {H}      0)
    ( {s}       {H}      0)
    ( {L}     {H}      0)

    (-{L}     0           {z})
    (-{s}       0           {z})
    (-{rw}      0           {z})
    ( {rw}      0           {z})
    ( {s}       0           {z})
    ( {L}     0           {z})
    (-{c:.8f} {c:.8f}  {z})
    ( 0          {rw}       {z})
    ( {c:.8f} {c:.8f}  {z})
    (-{s}       {s}        {z})
    ( 0          {s}        {z})
    ( {s}       {s}        {z})
    (-{L}     {s}        {z})
    ( {L}     {s}        {z})
    (-{L}     {H}      {z})
    (-{s}       {H}      {z})
    ( 0          {H}      {z})
    ( {s}       {H}      {z})
    ( {L}     {H}      {z})
);

blocks
(
    hex (1 2 6 9 20 21 25 28)    (30 12 1) simpleGrading (0.02 1 1)
    hex (9 6 7 10 28 25 26 29)   (30 12 1) simpleGrading (0.02 1 1)
    hex (10 7 8 11 29 26 27 30)  (30 12 1) simpleGrading (0.02 1 1)
    hex (11 8 3 4 30 27 22 23)   (30 12 1) simpleGrading (0.02 1 1)

    hex (0 1 9 12 19 20 28 31)   ({nL} 12 1) simpleGrading (0.2 1 1)
    hex (12 9 15 14 31 28 34 33) ({nL} {nV} 1) simpleGrading (0.2 0.25 1)
    hex (9 10 16 15 28 29 35 34) (12 {nV} 1) simpleGrading (1 0.25 1)
    hex (10 11 17 16 29 30 36 35)(12 {nV} 1) simpleGrading (1 0.25 1)
    hex (11 13 18 17 30 32 37 36)({nL} {nV} 1) simpleGrading (5 0.25 1)
    hex (4 5 13 11 23 24 32 30)  ({nL} 12 1) simpleGrading (5 1 1)
);

edges
(
    arc 2 6 origin (0 0 0)
    arc 6 7 origin (0 0 0)
    arc 7 8 origin (0 0 0)
    arc 8 3 origin (0 0 0)
    arc 21 25 origin (0 0 {z})
    arc 25 26 origin (0 0 {z})
    arc 26 27 origin (0 0 {z})
    arc 27 22 origin (0 0 {z})
);

boundary
(
    inlet
    {{
        type patch;
        faces ((0 12 31 19) (12 14 33 31));
    }}
    outlet
    {{
        type patch;
        faces ((5 13 32 24) (13 18 37 32));
    }}
    plate
    {{
        type wall;
        faces ((14 15 34 33) (15 16 35 34) (16 17 36 35) (17 18 37 36));
    }}
    wire
    {{
        type wall;
        faces ((2 6 25 21) (6 7 26 25) (7 8 27 26) (8 3 22 27));
    }}
    sym
    {{
        type symmetry;
        faces ((0 1 20 19) (1 2 21 20) (3 4 23 22) (4 5 24 23));
    }}
);

defaultPatch
{{
    name frontAndBack;
    type empty;
}}
"""
open(os.path.join(case, "system", "blockMeshDict"), "w").write(bm)
print(f"generated {case}: rw={rw}, H={H}, L={L}, nV={nV}, nL={nL}")
