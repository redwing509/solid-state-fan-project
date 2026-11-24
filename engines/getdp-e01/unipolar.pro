// Coupled Poisson + unipolar drift, Picard lag on E = -grad V.
// One system so charge enters Poisson as Dof{r}. Fixed step count.
// Backward-Euler time term (rho - rho_prev)/dt damps the lagged update
// (t1300u; METHOD.md). It cancels at a steady state.
// h_mesh, n_steps, inv_dt, mon_r1 and mon_r2 must be set by the wrapper
// before this Include.

Function {
  // Weak (volume) wire-current weight: phi = 1 for r <= mon_r1, 0 for
  // r >= mon_r2, linear between; grad phi = -r_hat / (mon_r2 - mon_r1).
  mon_rr[] = Sqrt[X[]*X[] + Y[]*Y[]] + 1e-30;
  mon_in[] = (mon_rr[] > mon_r1 && mon_rr[] < mon_r2) ? 1.0 : 0.0;
  mon_gphi[] = -mon_in[] * XYZ[] / (mon_rr[] * (mon_r2 - mon_r1));
}

Jacobian {
  { Name Vol;
    Case { { Region All; Jacobian Vol; } }
  }
  { Name Sur;
    Case { { Region All; Jacobian Sur; } }
  }
}

Integration {
  { Name I1;
    Case {
      { Type Gauss;
        Case {
          { GeoElement Point; NumberOfPoints 1; }
          { GeoElement Line; NumberOfPoints 4; }
          { GeoElement Triangle; NumberOfPoints 4; }
          { GeoElement Quadrangle; NumberOfPoints 4; }
        }
      }
    }
  }
}

Constraint {
  { Name Voltage;
    Case {
      { Region Emitter; Type Assign; Value V0; }
      { Region Collector; Type Assign; Value 0.0; }
    }
  }
  // Separate constraint so the Laplace pre-solve is not poisoned by Type Init
  // (that combination returned NaN on the wire-plate mesh; METHOD.md).
  { Name VoltageInit;
    Case {
      { Region Emitter; Type Assign; Value V0; }
      { Region Collector; Type Assign; Value 0.0; }
      { Region Domain; Type Init; Value use_v_init * V_laplace[]; }
    }
  }
  { Name Charge;
    Case {
      { Region Emitter; Type Assign; Value rho_a; }
    }
  }
}

FunctionSpace {
  { Name Hgrad_V_L; Type Form0;
    BasisFunction {
      { Name snv; NameOfCoef vn; Function BF_Node;
        Support Domain; Entity NodesOf[All]; }
    }
    Constraint {
      { NameOfCoef vn; EntityType NodesOf; NameOfConstraint Voltage; }
    }
  }
  { Name Hgrad_V; Type Form0;
    BasisFunction {
      { Name snv; NameOfCoef vn; Function BF_Node;
        Support Domain; Entity NodesOf[All]; }
    }
    Constraint {
      { NameOfCoef vn; EntityType NodesOf; NameOfConstraint VoltageInit; }
    }
  }
  { Name Hgrad_Rho; Type Form0;
    BasisFunction {
      { Name snr; NameOfCoef rn; Function BF_Node;
        Support Domain; Entity NodesOf[All]; }
    }
    Constraint {
      { NameOfCoef rn; EntityType NodesOf; NameOfConstraint Charge; }
    }
  }
}

Formulation {
  { Name Unipolar; Type FemEquation;
    Quantity {
      { Name v; Type Local; NameOfSpace Hgrad_V; }
      { Name r; Type Local; NameOfSpace Hgrad_Rho; }
    }
    Equation {
      // Poisson: div(eps0 grad v) = r, i.e. (eps0 grad v, grad w) = (r, w)
      // Equivalent Poisson: -div(grad v) = r/eps0. The eps0-weighted stiffness
      // form produced a NaN MUMPS solve on the wire-plate mesh (METHOD.md).
      Galerkin { [ Dof{d v} , {d v} ];
        In Domain; Jacobian Vol; Integration I1; }
      Galerkin { [ -Dof{r} / eps0 , {v} ];
        In Domain; Jacobian Vol; Integration I1; }
      // Transport, non-conservative form of div(r * mu * E)=0 with
      // E=-{d v} and div E = r/eps0 lagged from the last saved solution:
      // (mu E · grad r, w) + (mu r_lag / eps0 * r, w) = 0.
      Galerkin { [ -mu_ion * CompX[{d v}] * CompX[Dof{d r}] , {r} ];
        In Domain; Jacobian Vol; Integration I1; }
      Galerkin { [ -mu_ion * CompY[{d v}] * CompY[Dof{d r}] , {r} ];
        In Domain; Jacobian Vol; Integration I1; }
      Galerkin { [ mu_ion / eps0 * {r} * Dof{r} , {r} ];
        In Domain; Jacobian Vol; Integration I1; }
      // Backward-Euler time term; {r} is the previous step's solution.
      Galerkin { [ inv_dt * Dof{r} , {r} ];
        In Domain; Jacobian Vol; Integration I1; }
      Galerkin { [ -inv_dt * {r} , {r} ];
        In Domain; Jacobian Vol; Integration I1; }
      // Consistent SUPG, τ = h / (2|μ E|+ε), written as four single-Dof
      // terms because GetDP allows only one Dof{} per expression.
      Galerkin { [
          (h_mesh / (2.0 * mu_ion * (Sqrt[SquNorm[{d v}]] + 1e-30) + 1e-30)) *
          mu_ion * CompX[{d v}] * mu_ion * CompX[{d v}] * CompX[Dof{d r}]
        , CompX[{d r}] ]; In Domain; Jacobian Vol; Integration I1; }
      Galerkin { [
          (h_mesh / (2.0 * mu_ion * (Sqrt[SquNorm[{d v}]] + 1e-30) + 1e-30)) *
          mu_ion * CompX[{d v}] * mu_ion * CompY[{d v}] * CompX[Dof{d r}]
        , CompY[{d r}] ]; In Domain; Jacobian Vol; Integration I1; }
      Galerkin { [
          (h_mesh / (2.0 * mu_ion * (Sqrt[SquNorm[{d v}]] + 1e-30) + 1e-30)) *
          mu_ion * CompY[{d v}] * mu_ion * CompX[{d v}] * CompY[Dof{d r}]
        , CompX[{d r}] ]; In Domain; Jacobian Vol; Integration I1; }
      Galerkin { [
          (h_mesh / (2.0 * mu_ion * (Sqrt[SquNorm[{d v}]] + 1e-30) + 1e-30)) *
          mu_ion * CompY[{d v}] * mu_ion * CompY[{d v}] * CompY[Dof{d r}]
        , CompY[{d r}] ]; In Domain; Jacobian Vol; Integration I1; }
    }
  }
  { Name Laplace; Type FemEquation;
    Quantity { { Name v; Type Local; NameOfSpace Hgrad_V_L; } }
    Equation {
      Galerkin { [ Dof{d v} , {d v} ];
        In Domain; Jacobian Vol; Integration I1; }
    }
  }
}

Resolution {
  { Name Laplace;
    System { { Name L; NameOfFormulation Laplace; } }
    Operation { Generate[L]; Solve[L]; SaveSolution[L]; }
  }
  { Name Unipolar;
    System {
      { Name U; NameOfFormulation Unipolar; }
    }
    Operation {
      InitSolution[U];
      // Persist the Type Init guess so the first transport pass has E=-grad V.
      SaveSolution[U];
      // Only the start and the final step are written to case.res; the
      // monitor records Q and I_vol at every step.
      For it In {1:n_steps}
        Generate[U]; Solve[U];
        PostOperation[Monitor];
      EndFor
      SaveSolution[U];
    }
  }
}

PostProcessing {
  { Name Laplace; NameOfFormulation Laplace;
    Quantity {
      { Name v; Value { Term { [ {v} ]; In Domain; Jacobian Vol; } } }
    }
  }
  { Name Unipolar; NameOfFormulation Unipolar;
    Quantity {
      { Name v; Value { Term { [ {v} ]; In Domain; Jacobian Vol; } } }
      { Name e; Value { Term { [ -{d v} ]; In Domain; Jacobian Vol; } } }
      { Name r; Value { Term { [ {r} ]; In Domain; Jacobian Vol; } } }
      { Name I_emitter; Value {
          Integral { [ -mu_ion * {r} * ((-{d v}) * Normal[]) ];
            In Emitter; Jacobian Sur; Integration I1; }
        }
      }
      { Name I_collector; Value {
          Integral { [ mu_ion * {r} * ((-{d v}) * Normal[]) ];
            In Collector; Jacobian Sur; Integration I1; }
        }
      }
      // I_vol = -int rho mu E . grad(phi) dA = int mu rho grad(v) . grad(phi) dA.
      { Name I_vol; Value {
          Integral { [ mu_ion * {r} * ({d v} * mon_gphi[]) ];
            In Domain; Jacobian Vol; Integration I1; }
        }
      }
      { Name Q_rho; Value {
          Integral { [ {r} ]; In Domain; Jacobian Vol; Integration I1; }
        }
      }
      // Current per unit depth from a volume sample: I(r)=2 π r μ ρ |E|.
      // The Dirichlet-edge integral I_emitter is kept but is not the official
      // current (first-order {d v} vanishes on that edge).
      { Name I_r002; Value { Term { [ 2*Pi * 0.002 * mu_ion * {r} * Sqrt[SquNorm[{d v}]] ]; In Domain; Jacobian Vol; } } }
      { Name I_r005; Value { Term { [ 2*Pi * 0.005 * mu_ion * {r} * Sqrt[SquNorm[{d v}]] ]; In Domain; Jacobian Vol; } } }
      { Name I_r01;  Value { Term { [ 2*Pi * 0.01  * mu_ion * {r} * Sqrt[SquNorm[{d v}]] ]; In Domain; Jacobian Vol; } } }
      { Name I_r02;  Value { Term { [ 2*Pi * 0.02  * mu_ion * {r} * Sqrt[SquNorm[{d v}]] ]; In Domain; Jacobian Vol; } } }
      { Name I_r05;  Value { Term { [ 2*Pi * 0.05  * mu_ion * {r} * Sqrt[SquNorm[{d v}]] ]; In Domain; Jacobian Vol; } } }
    }
  }
}

PostOperation {
  { Name LaplaceMap; NameOfPostProcessing Laplace;
    Operation {
      Print[ v, OnElementsOf Domain, File "v_init.pos" ];
      Print[ v, OnPoint {probe_x, probe_y, 0}, Format Table, File "v_laplace_probe.dat" ];
    }
  }
  { Name Monitor; NameOfPostProcessing Unipolar;
    Operation {
      Print[ Q_rho[Domain], OnGlobal, Format Table, File >> "monitor_Q.dat" ];
      Print[ I_vol[Domain], OnGlobal, Format Table, File >> "monitor_I.dat" ];
    }
  }
  { Name Map; NameOfPostProcessing Unipolar;
    Operation {
      Print[ I_emitter[Emitter], OnGlobal, Format Table, File "I_emitter.dat" ];
      Print[ I_collector[Collector], OnGlobal, Format Table, File "I_collector.dat" ];
      Print[ Q_rho[Domain], OnGlobal, Format Table, File "Q_rho.dat" ];
      Print[ I_vol[Domain], OnGlobal, Format Table, File "I_vol.dat" ];
      Print[ v, OnPoint {probe_x, probe_y, 0}, Format Table, File "v_probe.dat" ];
      Print[ e, OnPoint {probe_x, probe_y, 0}, Format Table, File "e_probe.dat" ];
      Print[ r, OnPoint {probe_x, probe_y, 0}, Format Table, File "r_probe.dat" ];
      Print[ v, OnPoint {0.002, 0, 0}, Format Table, File "v_r002.dat" ];
      Print[ e, OnPoint {0.002, 0, 0}, Format Table, File "e_r002.dat" ];
      Print[ r, OnPoint {0.002, 0, 0}, Format Table, File "r_r002.dat" ];
      Print[ I_r002, OnPoint {0.002, 0, 0}, Format Table, File "I_r002.dat" ];
      Print[ v, OnPoint {0.005, 0, 0}, Format Table, File "v_r005.dat" ];
      Print[ e, OnPoint {0.005, 0, 0}, Format Table, File "e_r005.dat" ];
      Print[ r, OnPoint {0.005, 0, 0}, Format Table, File "r_r005.dat" ];
      Print[ I_r005, OnPoint {0.005, 0, 0}, Format Table, File "I_r005.dat" ];
      Print[ v, OnPoint {0.01, 0, 0}, Format Table, File "v_r01.dat" ];
      Print[ I_r01, OnPoint {0.01, 0, 0}, Format Table, File "I_r01.dat" ];
      Print[ v, OnPoint {0.02, 0, 0}, Format Table, File "v_r02.dat" ];
      Print[ e, OnPoint {0.02, 0, 0}, Format Table, File "e_r02.dat" ];
      Print[ r, OnPoint {0.02, 0, 0}, Format Table, File "r_r02.dat" ];
      Print[ I_r02, OnPoint {0.02, 0, 0}, Format Table, File "I_r02.dat" ];
      Print[ v, OnPoint {0.05, 0, 0}, Format Table, File "v_r05.dat" ];
      Print[ e, OnPoint {0.05, 0, 0}, Format Table, File "e_r05.dat" ];
      Print[ r, OnPoint {0.05, 0, 0}, Format Table, File "r_r05.dat" ];
      Print[ I_r05, OnPoint {0.05, 0, 0}, Format Table, File "I_r05.dat" ];
    }
  }
}
