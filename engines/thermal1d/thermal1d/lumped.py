"""Lumped-capacitance model  rho*c*V dT/dt = h*A*(T_inf - T) + P,
integrated with the theta method; exact solution for verification."""
from __future__ import annotations

import numpy as np


def lumped_exact(t, T_i, T_inf, tau, P_over_hA=0.0):
    Teq = T_inf + P_over_hA
    return Teq + (T_i - Teq) * np.exp(-np.asarray(t, dtype=float) / tau)


def lumped_solve(T_i, T_inf, tau, t_end, dt, theta=0.5, P_over_hA=0.0):
    """Return (t, T). tau = rho*c*V/(h*A)."""
    n = int(np.ceil(t_end / dt - 1e-12))
    t = np.linspace(0.0, n * dt, n + 1)
    T = np.empty(n + 1); T[0] = T_i
    Teq = T_inf + P_over_hA
    g = dt / tau
    for i in range(n):
        T[i + 1] = (T[i] + g * ((1 - theta) * (Teq - T[i]) + theta * Teq)) / (1 + g * theta)
    return t, T
