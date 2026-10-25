"""Richardson extrapolation and Grid Convergence Index.

Roache, P.J. (1994) J. Fluids Eng. 116:405-413; Roache (1998) Verification and
Validation in Computational Science and Engineering; Celik et al. (2008)
J. Fluids Eng. 130:078001 (ASME procedure); ASME V&V 20-2009.
Constant refinement ratio r, three solutions f1 (fine), f2, f3 (coarse).
"""
from __future__ import annotations

import math


def gci3(f1, f2, f3, r, Fs=1.25):
    e21 = f2 - f1; e32 = f3 - f2
    if e21 == 0 or e32 == 0 or e32 / e21 <= 0:
        raise ValueError("non-monotone convergence; GCI not defined")
    p = math.log(e32 / e21) / math.log(r)
    f_ext = f1 + (f1 - f2) / (r ** p - 1.0)
    gci_fine = Fs * abs(e21 / f1) / (r ** p - 1.0)
    gci_coarse = Fs * abs(e32 / f2) / (r ** p - 1.0)
    asym = gci_coarse / (r ** p * gci_fine)   # ~1 in the asymptotic range
    return {"p": p, "f_ext": f_ext, "gci_fine": gci_fine, "gci_coarse": gci_coarse,
            "asymptotic_ratio": asym, "e21": e21, "e32": e32}


def observed_order(errors, hs):
    """Least-squares slope of log(error) vs log(h) plus pairwise orders."""
    import numpy as np
    le = np.log(np.asarray(errors)); lh = np.log(np.asarray(hs))
    slope = float(np.polyfit(lh, le, 1)[0])
    pair = [float((le[i] - le[i + 1]) / (lh[i] - lh[i + 1])) for i in range(len(le) - 1)]
    return slope, pair
