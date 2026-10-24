"""thermal1d: in-house 1-D transient conduction / lumped-capacitance engine.

Independent of OpenFOAM: inputs come from documented geometry, properties and
boundary conditions only. See README.md and VERIFICATION.md.
"""
from .solver import Boundary, Problem, Result, solve, steady, tridiag_solve, uniform_grid
from .lumped import lumped_solve, lumped_exact

__all__ = ["Boundary", "Problem", "Result", "solve", "steady", "tridiag_solve",
           "uniform_grid", "lumped_solve", "lumped_exact"]
__version__ = "1.0.0"
