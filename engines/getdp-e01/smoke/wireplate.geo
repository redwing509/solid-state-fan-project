// Nov 1 / E-01 original OpenFOAM half-domain, 2-D (unit depth = A/m).
// Source: of-runs/out-eonly/E8/system/blockMeshDict (convertToMeters 0.001).
// Wire centre at origin, radius 39.5 um; plate at y=-0.02004 m;
// x=0..0.32 m, y=-0.02004..0.06 m, symmetry at x=0.
// lc_factor = 1 (smoke / coarse), 0.5, 0.25 for the mesh study.
If (!Exists(lc_factor))
  lc_factor = 1;
EndIf

rw = 39.5e-6;
xmin = 0.0;
xmax = 0.32;
ymin = -0.02004;
ymax = 0.06;
lc_w = 8.0e-6 * lc_factor;   // ~5 points across a radius at lc_factor=1
lc_far = 0.008 * lc_factor;

Point(1) = {0, 0, 0, lc_w};
// wire half-circle in x>=0, four points (bottom, mid, 45 below, 45 above, top)
Point(2) = {0, -rw, 0, lc_w};
Point(3) = {rw*0.7071067811865476, -rw*0.7071067811865476, 0, lc_w};
Point(4) = {rw, 0, 0, lc_w};
Point(5) = {rw*0.7071067811865476,  rw*0.7071067811865476, 0, lc_w};
Point(6) = {0,  rw, 0, lc_w};

Point(10) = {0, ymin, 0, lc_far};          // plate at symmetry
Point(11) = {xmax, ymin, 0, lc_far};       // plate at right
Point(12) = {xmax, ymax, 0, lc_far};       // top-right
Point(13) = {0, ymax, 0, lc_far};          // top at symmetry

Circle(1) = {2, 1, 3};
Circle(2) = {3, 1, 4};
Circle(3) = {4, 1, 5};
Circle(4) = {5, 1, 6};

Line(10) = {6, 13};   // symmetry, wire to top
Line(11) = {13, 12};  // top
Line(12) = {12, 11};  // right
Line(13) = {11, 10};  // plate
Line(14) = {10, 2};   // symmetry, plate to wire

Line Loop(1) = {1, 2, 3, 4, 10, 11, 12, 13, 14};
Plane Surface(1) = {1};

Physical Line(1) = {1, 2, 3, 4}; // Wire / emitter
Physical Line(2) = {13};         // Plate / collector
Physical Line(3) = {12};         // Right
Physical Line(4) = {11};         // Top
Physical Line(5) = {10, 14};     // Symmetry
Physical Surface(6) = {1};



// Refine toward the wire
Field[1] = Distance;
Field[1].PointsList = {1};
Field[2] = Threshold;
Field[2].InField = 1;
Field[2].SizeMin = lc_w;
Field[2].SizeMax = lc_far;
Field[2].DistMin = 4*rw;
Field[2].DistMax = 0.04;
Background Field = 2;

Mesh.Algorithm = 6;
Mesh.ElementOrder = 1;
