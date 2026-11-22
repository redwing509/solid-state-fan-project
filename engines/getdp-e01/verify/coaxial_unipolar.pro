// Coaxial unipolar known-solution case (t1244u). PUSH=0. Model-only.
V0 = 30000;
rho_a = 1e-5;
mu_ion = 1.8e-4;
eps0 = 8.854e-12;
h_mesh = 8e-5;
n_picard = 40;
probe_x = 0.01;
probe_y = 0.0;
a_coax = 0.001;
b_coax = 0.1;
// Analytic Laplace field used only as the first Picard guess (METHOD.md).
Function {
  rxy[] = Sqrt[X[]*X[] + Y[]*Y[]] + 1e-30;
  V_laplace[] = V0 * Log[b_coax / rxy[]] / Log[b_coax / a_coax];
}
use_v_init = 1;

Group {
  Emitter = Region[1];
  Collector = Region[2];
  Outflow = Region[{2}];
  Domain = Region[3];
  ProbeContour = Region[{}];
}

Include "../unipolar.pro";
