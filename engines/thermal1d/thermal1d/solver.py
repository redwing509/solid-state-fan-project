"""Vertex-centred finite-volume solver for

    rho_c(x) dT/dt = d/dx( k(x) dT/dx ) + s(x, t),   x in [x_0, x_N]

with Dirichlet, Neumann (prescribed inward heat flux) or Robin (convective)
boundaries and theta-method time integration (theta=1 implicit Euler,
theta=0.5 Crank-Nicolson).

Nodes sit on both boundaries; node i owns the control volume between the
midpoints of its neighbouring intervals (half volumes at the ends). Face
conductivity is k evaluated at the interval midpoint. Every interior face flux
appears with opposite sign in the two adjacent control volumes, so the scheme
conserves energy exactly (to round-off); boundary heat inflow is accumulated
with the same theta weighting so that

    E(t_n) - E(0) = sum_n dt * [ theta*Q(n+1) + (1-theta)*Q(n) ]

holds to machine precision, where Q is the total boundary + source heat rate
(per unit cross-sectional area, W/m^2).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional, Sequence, Union

import numpy as np

try:  # optional speed-up
    from scipy.linalg import solve_banded as _solve_banded
except ImportError:  # pragma: no cover
    _solve_banded = None

Num = Union[float, Callable[[float], float]]


def _val(f: Num, t: float) -> float:
    return float(f(t)) if callable(f) else float(f)


@dataclass
class Boundary:
    """Boundary condition.

    kind = "dirichlet": T = value(t)
    kind = "flux":      heat flux INTO the domain = value(t)  [W/m^2]
    kind = "robin":     heat flux INTO the domain = h*(T_inf(t) - T_wall)
    """
    kind: str
    value: Num = 0.0
    h: float = 0.0
    T_inf: Num = 0.0

    def __post_init__(self):
        if self.kind not in ("dirichlet", "flux", "robin"):
            raise ValueError(f"unknown boundary kind {self.kind!r}")
        if self.kind == "robin" and self.h <= 0:
            raise ValueError("robin boundary needs h > 0")


@dataclass
class Problem:
    x: np.ndarray                      # node coordinates (strictly increasing), m
    k: Union[float, Callable]          # W/(m K); callable k(x)
    rho_c: Union[float, Callable]      # J/(m^3 K); callable rho_c(x)
    left: Boundary
    right: Boundary
    T0: Union[float, Callable]         # initial temperature (K); callable T0(x)
    source: Optional[Callable] = None  # s(x, t) W/m^3, vectorised in x

    def __post_init__(self):
        self.x = np.asarray(self.x, dtype=float)
        if self.x.ndim != 1 or self.x.size < 3 or np.any(np.diff(self.x) <= 0):
            raise ValueError("x must be a strictly increasing 1-D array with >= 3 nodes")


@dataclass
class Result:
    x: np.ndarray
    t: np.ndarray                 # output times
    T: np.ndarray                 # shape (len(t), N)
    energy: np.ndarray            # stored energy per area, J/m^2, at output times
    heat_in: np.ndarray           # cumulative heat input per area, J/m^2 (boundaries + source)
    heat_in_left: np.ndarray
    heat_in_right: np.ndarray
    volumes: np.ndarray           # control-volume lengths (m)
    info: dict = field(default_factory=dict)

    def mean_T(self, i: int = -1) -> float:
        """Volume-weighted (energy-consistent) mean temperature at output i."""
        return float(np.dot(self.volumes, self.T[i]) / self.volumes.sum())

    def max_T(self, i: int = -1) -> float:
        return float(self.T[i].max())


def uniform_grid(x0: float, x1: float, n_cells: int) -> np.ndarray:
    return np.linspace(x0, x1, n_cells + 1)


def tridiag_solve(a, b, c, d):
    """Tridiagonal solve. a: sub (a[0] unused), b: diag, c: super (c[-1] unused).

    Uses scipy.linalg.solve_banded (LAPACK gtsv-style banded LU) when SciPy is
    installed, otherwise the Thomas algorithm below (identical results to round-off).
    """
    if _solve_banded is not None:
        ab = np.zeros((3, len(b)))
        ab[0, 1:] = c[:-1]; ab[1] = b; ab[2, :-1] = a[1:]
        return _solve_banded((1, 1), ab, d)
    return thomas(a, b, c, d)


def thomas(a, b, c, d):
    """Thomas algorithm (pure NumPy/Python fallback)."""
    n = len(b)
    cp = np.empty(n)
    dp = np.empty(n)
    cp[0] = c[0] / b[0]
    dp[0] = d[0] / b[0]
    for i in range(1, n):
        m = b[i] - a[i] * cp[i - 1]
        cp[i] = c[i] / m if i < n - 1 else 0.0
        dp[i] = (d[i] - a[i] * dp[i - 1]) / m
    out = np.empty(n)
    out[-1] = dp[-1]
    for i in range(n - 2, -1, -1):
        out[i] = dp[i] - cp[i] * out[i + 1]
    return out


def _field(f, x):
    return np.full_like(x, float(f)) if not callable(f) else np.asarray(f(x), dtype=float) * np.ones_like(x)


def _operator(p: Problem):
    x = p.x
    hx = np.diff(x)
    xm = 0.5 * (x[:-1] + x[1:])
    kf = _field(p.k, xm)                       # face conductivities
    G = kf / hx                                # face conductances
    V = np.zeros_like(x)
    V[:-1] += 0.5 * hx
    V[1:] += 0.5 * hx
    C = _field(p.rho_c, x) * V                 # nodal heat capacities per area
    return G, V, C


def _src(p: Problem, t: float, V):
    if p.source is None:
        return np.zeros_like(V)
    return np.asarray(p.source(p.x, t), dtype=float) * np.ones_like(V) * V


def _bc_rate(b: Boundary, Tw: float, t: float) -> float:
    """Heat rate into domain at a non-Dirichlet boundary (explicit evaluation)."""
    if b.kind == "flux":
        return _val(b.value, t)
    return b.h * (_val(b.T_inf, t) - Tw)


def solve(p: Problem, t_end: float, dt: float, theta: float = 0.5,
          t_out: Optional[Sequence[float]] = None) -> Result:
    """Integrate from t=0 to t_end with fixed step dt (last step shortened)."""
    if not (0.0 <= theta <= 1.0):
        raise ValueError("theta must be in [0, 1]")
    if dt <= 0 or t_end < 0:
        raise ValueError("dt must be > 0 and t_end >= 0")
    G, V, C = _operator(p)
    N = p.x.size
    T = _field(p.T0, p.x).copy()
    if p.left.kind == "dirichlet":
        T[0] = _val(p.left.value, 0.0)
    if p.right.kind == "dirichlet":
        T[-1] = _val(p.right.value, 0.0)

    t_out = sorted(set([0.0, float(t_end)] + ([float(s) for s in t_out] if t_out else [])))
    outs_t, outs_T, outs_E, outs_Q, outs_QL, outs_QR = [], [], [], [], [], []
    Qcum = QL = QR = 0.0

    def record(t):
        outs_t.append(t); outs_T.append(T.copy()); outs_E.append(float(np.dot(C, T)))
        outs_Q.append(Qcum); outs_QL.append(QL); outs_QR.append(QR)

    def net_conduction(Tv):
        r = np.zeros(N)
        f = G * (Tv[1:] - Tv[:-1])      # flux from i+1 into i (per face)
        r[:-1] += f
        r[1:] -= f
        return r

    t = 0.0
    k_out = 0
    if t_out[0] == 0.0:
        record(0.0); k_out = 1
    nsteps = 0
    while t < t_end - 1e-14 * max(1.0, t_end):
        step = min(dt, t_end - t)
        if k_out < len(t_out) and t + step > t_out[k_out] + 1e-14 * max(1.0, t_end):
            step = t_out[k_out] - t
        t1 = t + step
        # explicit part
        Ln = net_conduction(T)
        Sn = _src(p, t, V); S1 = _src(p, t1, V)
        rhs = C * T + step * ((1 - theta) * (Ln + Sn) + theta * S1)
        a = np.zeros(N); b = C.copy(); c = np.zeros(N)
        # implicit conduction
        b[:-1] += step * theta * G; b[1:] += step * theta * G
        c[:-1] -= step * theta * G; a[1:] -= step * theta * G
        # boundaries
        qn = {}
        for side, idx in (("left", 0), ("right", N - 1)):
            bc = getattr(p, side)
            if bc.kind == "flux":
                qn[side] = _val(bc.value, t); q1 = _val(bc.value, t1)
                rhs[idx] += step * ((1 - theta) * qn[side] + theta * q1)
            elif bc.kind == "robin":
                qn[side] = _bc_rate(bc, T[idx], t)
                rhs[idx] += step * ((1 - theta) * qn[side] + theta * bc.h * _val(bc.T_inf, t1))
                b[idx] += step * theta * bc.h
        Tn = T.copy()
        for side, idx in (("left", 0), ("right", N - 1)):
            bc = getattr(p, side)
            if bc.kind == "dirichlet":
                a[idx] = 0.0; c[idx] = 0.0; b[idx] = 1.0
                rhs[idx] = _val(bc.value, t1)
        T = tridiag_solve(a, b, c, rhs)
        # boundary heat actually entering (theta-weighted, consistent with update)
        L1 = net_conduction(T)
        dQ = {}
        for side, idx in (("left", 0), ("right", N - 1)):
            bc = getattr(p, side)
            if bc.kind == "dirichlet":
                # residual of the Dirichlet node's control-volume balance
                dQ[side] = C[idx] * (T[idx] - Tn[idx]) - step * (
                    (1 - theta) * (Ln[idx] + Sn[idx]) + theta * (L1[idx] + S1[idx]))
            elif bc.kind == "flux":
                dQ[side] = step * ((1 - theta) * qn[side] + theta * _val(bc.value, t1))
            else:
                dQ[side] = step * ((1 - theta) * qn[side] + theta * _bc_rate(bc, T[idx], t1))
        dS = step * ((1 - theta) * Sn.sum() + theta * S1.sum())
        QL += dQ["left"]; QR += dQ["right"]; Qcum += dQ["left"] + dQ["right"] + dS
        t = t1; nsteps += 1
        if k_out < len(t_out) and abs(t - t_out[k_out]) <= 1e-12 * max(1.0, t_end):
            record(t_out[k_out]); k_out += 1
    return Result(x=p.x.copy(), t=np.array(outs_t), T=np.array(outs_T), energy=np.array(outs_E),
                  heat_in=np.array(outs_Q), heat_in_left=np.array(outs_QL), heat_in_right=np.array(outs_QR),
                  volumes=V, info={"steps": nsteps, "theta": theta, "dt": dt, "nodes": N})


def steady(p: Problem) -> np.ndarray:
    """Steady solution (no time derivative) of the same discrete operator."""
    G, V, C = _operator(p)
    N = p.x.size
    a = np.zeros(N); b = np.zeros(N); c = np.zeros(N)
    b[:-1] += G; b[1:] += G; c[:-1] -= G; a[1:] -= G
    rhs = _src(p, 0.0, V)
    for side, idx in (("left", 0), ("right", N - 1)):
        bc = getattr(p, side)
        if bc.kind == "flux":
            rhs[idx] += _val(bc.value, 0.0)
        elif bc.kind == "robin":
            b[idx] += bc.h; rhs[idx] += bc.h * _val(bc.T_inf, 0.0)
        else:
            a[idx] = 0.0; c[idx] = 0.0; b[idx] = 1.0; rhs[idx] = _val(bc.value, 0.0)
    return tridiag_solve(a, b, c, rhs)
