// Nov 1 / E-01 original-domain unipolar current (t1244u). PUSH=0. Model-only.
V0 = 7540;
rho_a = 1.743e-4;
mu_ion = 2.3e-4;
eps0 = 8.85419e-12;
h_mesh = 8e-6;
n_picard = 40;
use_v_init = 0;
Function { V_laplace[] = 0.; }
// The runner enables use_v_init and GmshRead["v_init.pos"] after the Laplace pre-solve.
// Probe in the gap, on the symmetry plane below the wire (x=0, mid-gap).
probe_x = 0.0;
probe_y = -0.010;

Group {
  Emitter = Region[1];
  Collector = Region[2];
  Right = Region[3];
  Top = Region[4];
  SymmetryEdge = Region[5];
  Outflow = Region[{2, 3, 4}];
  Domain = Region[6];
  ProbeContour = Region[{}];
}

Include "../unipolar.pro";
