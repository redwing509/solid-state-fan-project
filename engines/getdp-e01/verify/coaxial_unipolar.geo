// Coaxial unipolar known-solution geometry (full annulus, unit depth).
// a=0.001 m, b=0.1 m. lc_factor = 1, 0.5, 0.25 for the mesh study.
If (!Exists(lc_factor))
  lc_factor = 1;
EndIf
a = 0.001;
b = 0.1;
lc_in = 0.00008 * lc_factor;
lc_out = 0.004 * lc_factor;

Point(1) = {0, 0, 0, lc_in};
Point(2) = { a, 0, 0, lc_in};
Point(3) = {0,  a, 0, lc_in};
Point(4) = {-a, 0, 0, lc_in};
Point(5) = {0, -a, 0, lc_in};
Point(6) = { b, 0, 0, lc_out};
Point(7) = {0,  b, 0, lc_out};
Point(8) = {-b, 0, 0, lc_out};
Point(9) = {0, -b, 0, lc_out};

Circle(1) = {2, 1, 3};
Circle(2) = {3, 1, 4};
Circle(3) = {4, 1, 5};
Circle(4) = {5, 1, 2};
Circle(5) = {6, 1, 7};
Circle(6) = {7, 1, 8};
Circle(7) = {8, 1, 9};
Circle(8) = {9, 1, 6};

Line Loop(1) = {1, 2, 3, 4};
Line Loop(2) = {5, 6, 7, 8};
Plane Surface(1) = {2, 1};

Physical Line(1) = {1, 2, 3, 4}; // Emitter (inner)
Physical Line(2) = {5, 6, 7, 8}; // Collector (outer)
Physical Surface(3) = {1};

Mesh.Algorithm = 6;
Mesh.ElementOrder = 1;
