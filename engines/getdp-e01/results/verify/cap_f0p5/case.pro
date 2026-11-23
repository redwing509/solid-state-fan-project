// Coaxial-capacitor electrostatics. Compare energy, V, and E to the exact
// 2-D (per unit length) formulas. Standalone GetDP 3.5 file; no includes.

Group {
  Inner = Region[1];
  Outer = Region[2];
  Dielectric = Region[3];
  Domain = Region[{Dielectric}];
}

Function {
  eps0 = 8.854187818e-12; // same constant as official GetDP template
  epsr[] = 1.0;
}

Constraint {
  { Name Voltage;
    Case {
      { Region Inner; Type Assign; Value 1.0; }
      { Region Outer; Type Assign; Value 0.0; }
    }
  }
}

Jacobian {
  { Name Vol;
    Case {
      { Region All; Jacobian Vol; }
    }
  }
}

Integration {
  { Name I1;
    Case {
      { Type Gauss;
        Case {
          { GeoElement Point; NumberOfPoints 1; }
          { GeoElement Line; NumberOfPoints 3; }
          { GeoElement Triangle; NumberOfPoints 4; }
          { GeoElement Quadrangle; NumberOfPoints 4; }
        }
      }
    }
  }
}

FunctionSpace {
  { Name Hgrad_V; Type Form0;
    BasisFunction {
      { Name sn; NameOfCoef vn; Function BF_Node;
        Support Domain; Entity NodesOf[All]; }
    }
    Constraint {
      { NameOfCoef vn; EntityType NodesOf; NameOfConstraint Voltage; }
    }
  }
}

Formulation {
  { Name Electrostatics; Type FemEquation;
    Quantity {
      { Name v; Type Local; NameOfSpace Hgrad_V; }
    }
    Equation {
      Integral { [ eps0 * epsr[] * Dof{d v} , {d v} ];
        In Domain; Jacobian Vol; Integration I1; }
    }
  }
}

Resolution {
  { Name Electrostatics;
    System {
      { Name A; NameOfFormulation Electrostatics; }
    }
    Operation {
      Generate[A]; Solve[A]; SaveSolution[A];
    }
  }
}

PostProcessing {
  { Name Electrostatics; NameOfFormulation Electrostatics;
    PostQuantity {
      { Name v; Value {
          Term { [ {v} ]; In Domain; Jacobian Vol; }
        }
      }
      { Name e; Value {
          Term { [ -{d v} ]; In Domain; Jacobian Vol; }
        }
      }
      { Name energy; Value {
          Integral { [ 0.5 * eps0 * epsr[] * SquNorm[{d v}] ];
            In Domain; Jacobian Vol; Integration I1; }
        }
      }
    }
  }
}

PostOperation {
  { Name Map; NameOfPostProcessing Electrostatics;
    Operation {
      Print[ energy[Domain], OnGlobal, Format Table, File "energy.dat" ];
      Print[ v, OnPoint {0.03, 0, 0}, Format Table, File "v_probe.dat" ];
      Print[ e, OnPoint {0.03, 0, 0}, Format Table, File "e_probe.dat" ];
    }
  }
}
