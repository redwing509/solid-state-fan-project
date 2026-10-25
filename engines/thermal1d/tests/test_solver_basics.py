import numpy as np
import pytest

from thermal1d import Boundary, Problem, solve, steady, tridiag_solve, uniform_grid
from thermal1d.solver import thomas
from thermal1d.gci import gci3, observed_order


def test_thomas_matches_dense():
    rng = np.random.default_rng(0)
    n = 12
    a = rng.uniform(-1, 0, n); c = rng.uniform(-1, 0, n); b = 3 + rng.uniform(0, 1, n)
    a[0] = 0; c[-1] = 0
    d = rng.normal(size=n)
    M = np.diag(b) + np.diag(a[1:], -1) + np.diag(c[:-1], 1)
    np.testing.assert_allclose(thomas(a, b, c, d), np.linalg.solve(M, d), rtol=1e-12)
    np.testing.assert_allclose(tridiag_solve(a, b, c, d), np.linalg.solve(M, d), rtol=1e-12)


def test_uniform_state_is_preserved():
    x = uniform_grid(0, 1, 11)
    p = Problem(x, 1.0, 1.0, Boundary("flux", 0.0), Boundary("flux", 0.0), 300.0)
    r = solve(p, 1.0, 0.1)
    np.testing.assert_allclose(r.T, 300.0, atol=1e-12)


def test_bad_boundary_kind_rejected():
    with pytest.raises(ValueError):
        Boundary("nonsense", 1.0)


def test_gci_exact_quadratic():
    # f(h) = 1 + h^2 sampled at h = 1, 2, 4 -> p = 2, extrapolated value 1
    f1, f2, f3 = 1 + 1, 1 + 4, 1 + 16
    g = gci3(f1, f2, f3, 2.0)
    assert abs(g["p"] - 2.0) < 1e-12
    assert abs(g["f_ext"] - 1.0) < 1e-12
    slope, pair = observed_order([1.0, 0.25, 0.0625], [1.0, 0.5, 0.25])
    assert abs(slope - 2.0) < 1e-12 and all(abs(q - 2.0) < 1e-12 for q in pair)


def test_baseline_energy_balance():
    from thermal1d.baseline import run
    r = run(n_cells=128, dt=1e-2)
    assert abs(r["energy_residual_J_m2"]) < 1e-6
