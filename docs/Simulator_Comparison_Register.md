# Fan research — simulator and virtual-lab register

Updated October 21, 2026. Standing direction: seek broad, useful independent tests and compare matched results. Count only executed jobs as executed; model capability is not a result.

| Tool / implementation | Purpose | Current state | What a comparison can establish |
| --- | --- | --- | --- |
| Private Ionic Wind Virtual Lab | Supply/array/cost scenarios | Existing live planning interface; earlier arithmetic checks retained | Arithmetic sensitivity; unvalidated assumptions do not predict a real fan |
| OpenFOAM Foundation 4.1 EHD solver | Coupled charge, electrostatics, flow and heat | Full original case completed at 10 s, numerically reviewed; eight new controls queued | Thermal input mismatch found; experimental validation remains open |
| ngspice 44.2 | AC circuit representation of layered dielectric coupons | Executed 300 parameter cases: 75 each at 110/220/330/440 V RMS | Voltage division and displacement-current agreement for ideal linear capacitors |
| Separate 1D finite-volume field implementation | Variable-permittivity planar electric fields | Executed those same 300 cases on 20/40/80 interface-aligned grids | Numerical consistency with capacitor representation; exact piecewise-linear case does not validate complicated meshes |
| Closed-form layered-dielectric reference | Series capacitance / field reference | Calculated for the same cases | Reference calculation, not a separately validated commercial simulator |
| SciPy shooting and separate BVP collocation implementations | Coaxial fixed-charge corona electrical benchmark | 36 cases executed and compared | Electrical equations/current agreement; radial pressure balance gives no useful fan airflow |
| OpenCFD v2412 electrostaticSimpleFoam | Modern EHD and coaxial/ESP verification | Pinned runtime installed and solver built; initial reference cases completed; 216 electrical and 90 duct cases queued/running | First four queued electrical cases compared with exact solution; full mesh/scheme/parameter review and flow validation pending |
| COMSOL Electric Discharge + laminar flow | Corona, dielectric charging and flow | Official Ionic Wind tutorial identified; license not established | Potential independent multiphysics comparison after a matched, licensed run |
| Fluent point-to-ring EHD case | Paper-linked second EHD implementation | Public UDF/case identified; license/version/setup not established | Reproduce its experimental case before adapting fan geometry |
| Elmer FEM | Material permittivity and electrostatic/thermal FEM | Official source/example identified; not installed | Useful independent material-field checks; corona/charge/flow coupling needs implementation |
| FEniCSx | Independent custom FEM formulation | Official Poisson example identified; not installed | Dielectric Poisson validation, with charge transport/flow added separately |
| Qucs-S / ngspice | Converter and circuit analysis | Qucs-S front end not installed; ngspice core used separately | Requires a real converter model before supply-to-electrode performance claims |
| Phenomenological DBD OpenFOAM solver | Dielectric-barrier actuator force/flow | Public source reviewed; not installed | Different discharge physics; not interchangeable with DC corona fan results |

## Common comparison rules

Match geometry, mesh/accuracy targets, properties and their temperature/frequency, boundary conditions, electrode voltage/waveform, injected charge/onset treatment, gas state and output definitions. Compare current, field profiles, conservation, integrated flow, pressure and input power only where each implementation actually models them. Record signed and relative differences, reference uncertainty, solver tolerances and unsupported outputs. Agreement of models sharing assumptions is a consistency check, not independent physical proof.

Keep 110/220/330/440 V AC supply scenarios separate from high-voltage electrode tests. Material differences not represented by a model are pending, not zero-effect findings. A source-derived nominal property does not establish performance of an unknown grade or manufactured assembly.

Notify the user before heavy-load runs and jointly choose the compute. Local simulation utilization is capped at 50% CPU/GPU; do not treat GPU power caps as compute utilization caps.

## Primary sources

- Existing private lab: https://ionic-wind-virtual-lab.spokanelawncare.chatgpt.site
- OpenFOAM EHD source: https://github.com/nzhtbyn/buoyantBoussinesqPimpleEHDFoam
- Modern source and benchmark: https://github.com/swtbkim/electrostaticSimpleFoam
- ngspice documentation: https://ngspice.sourceforge.io/docs.html
- COMSOL: https://doc.comsol.com/6.4/doc/com.comsol.help.models.edis.ionic_wind/ionic_wind.html
- Fluent UDF/case: https://github.com/gyf135/EHD-in-point-to-ring-corona
- Elmer: https://github.com/ElmerCSC/elmerfem ; example https://github.com/ElmerCSC/elmer-elmag/blob/main/CapacitanceOfTwoBalls/case.sif
- FEniCSx: https://docs.fenicsproject.org/dolfinx/main/python/demos/demo_poisson.html
- Qucs-S: https://github.com/ra3xdh/qucs_s
- DBD solver: https://github.com/rulzco/phenomenological-dbdActuatorSolver
