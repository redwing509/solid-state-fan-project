"""Closed-form reference solutions used by the verification suite.

References
- Carslaw, H.S. & Jaeger, J.C. (1959) Conduction of Heat in Solids, 2nd ed., OUP:
  semi-infinite solid, constant surface flux (Sec. 2.9) and constant surface
  temperature (Sec. 2.4); slab Fourier series (Sec. 3.3).
- Incropera, F.P., DeWitt, D.P., Bergman, T.L., Lavine, A.S., Fundamentals of
  Heat and Mass Transfer, 6th ed. (2007), Ch. 3 (plane wall, convection BC),
  Ch. 5 (lumped capacitance, Eq. 5.6; semi-infinite solid, Eqs. 5.57-5.58).
"""
from __future__ import annotations

import math

import numpy as np

_erfc = np.vectorize(math.erfc)


def semi_infinite_flux(x, t, q, k, alpha, T_i):
    """Constant inward flux q at x=0 into a semi-infinite solid initially at T_i."""
    x = np.asarray(x, dtype=float)
    s = 2.0 * math.sqrt(alpha * t)
    return T_i + (2.0 * q / k) * math.sqrt(alpha * t / math.pi) * np.exp(-(x / s) ** 2) \
        - (q * x / k) * _erfc(x / s)


def semi_infinite_temp(x, t, T_s, alpha, T_i):
    """Surface suddenly held at T_s."""
    x = np.asarray(x, dtype=float)
    return T_s + (T_i - T_s) * (1.0 - _erfc(x / (2.0 * math.sqrt(alpha * t))))


def slab_flux_dirichlet(x, t, L, q, k, alpha, T_i, n_terms=400):
    """Slab 0<=x<=L, inward flux q at x=0, T=T_i held at x=L, initially T_i.

    T = T_i + q (L - x)/k - sum_n (2 q L / (k lambda_n^2)) cos(lambda_n x / L) exp(-lambda_n^2 alpha t / L^2)
    with lambda_n = (n + 1/2) pi  (separation of variables; steady part q(L-x)/k).
    """
    x = np.asarray(x, dtype=float)
    out = q * (L - x) / k
    for n in range(n_terms):
        lam = (n + 0.5) * math.pi
        out = out - (2.0 * q * L / (k * lam ** 2)) * np.cos(lam * x / L) * math.exp(-lam ** 2 * alpha * t / L ** 2)
    return T_i + out


def slab_dirichlet_cooling(x, t, L, alpha, T_i, T_w, n_terms=400):
    """Slab initially T_i, both faces suddenly at T_w (Carslaw & Jaeger 3.3)."""
    x = np.asarray(x, dtype=float)
    s = np.zeros_like(x)
    for n in range(n_terms):
        m = 2 * n + 1
        s += (4.0 / (m * math.pi)) * np.sin(m * math.pi * x / L) * math.exp(-(m * math.pi / L) ** 2 * alpha * t)
    return T_w + (T_i - T_w) * s


def plane_wall_convective(x, L, T1, h, T_inf, k):
    """Steady plane wall, T(0)=T1, -k dT/dx(L) = h (T(L) - T_inf). Linear profile."""
    x = np.asarray(x, dtype=float)
    Bi = h * L / k
    TL = (T1 + Bi * T_inf) / (1.0 + Bi)
    return T1 + (TL - T1) * x / L


def plane_wall_generation(x, L, qdot, k, T0, TL):
    """Steady plane wall with uniform generation, T(0)=T0, T(L)=TL."""
    x = np.asarray(x, dtype=float)
    return T0 + (TL - T0) * x / L + qdot * x * (L - x) / (2.0 * k)
