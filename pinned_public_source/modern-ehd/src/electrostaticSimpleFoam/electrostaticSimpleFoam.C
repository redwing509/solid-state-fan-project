// ---------------------------------------------------------------------------
//   =========                 |
//   \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
//    \\    /   O peration     |
//     \\  /    A nd           | www.openfoam.com
//      \\/     M anipulation  |
// ---------------------------------------------------------------------------
//     Copyright (C) 2011-2017 OpenFOAM Foundation
//     Copyright (C) 2019-2021 OpenCFD Ltd.
//     Copyright (C) 2026 Sangwoo Kim
// ---------------------------------------------------------------------------
// License
//     This file is part of electrostaticSimpleFoam, derived from the OpenFOAM
//     solvers simpleFoam and electrostaticFoam.
//
//     OpenFOAM is free software: you can redistribute it and/or modify it
//     under the terms of the GNU General Public License as published by
//     the Free Software Foundation, either version 3 of the License, or
//     (at your option) any later version.
//
//     OpenFOAM is distributed in the hope that it will be useful, but WITHOUT
//     ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
//     FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
//     for more details.
//
//     You should have received a copy of the GNU General Public License
//     along with this code.  If not, see <http://www.gnu.org/licenses/>.
// ---------------------------------------------------------------------------
// Application
//     electrostaticSimpleFoam
//
// Description
//     Steady-state solver for incompressible, turbulent flow coupled with
//     DC corona electrostatics (electrohydrodynamics, EHD).
//
//     Combines simpleFoam and electrostaticFoam:
//       - electric potential   : laplacian(V) = -rhoq/epsilon0
//       - electric field       : E = -grad(V)
//       - space charge         : div((U + muq*E)*rhoq) = div(Dq*grad(rhoq))
//       - momentum             : SIMPLE with EHD body force f = rhoq*E
//
//     Since simpleFoam solves the momentum equation divided by the fluid
//     density (kinematic pressure), the body force is added as
//     rhoq*E/rhoFluid [m/s^2].
//
//     Field naming (to avoid clashes with simpleFoam):
//       electrostaticFoam "phi" (potential)      -> "V"
//       electrostaticFoam "rho" (charge density) -> "rhoq"
//       electrostaticFoam "k"   (ion mobility)   -> "muq"
// ---------------------------------------------------------------------------

#include "fvCFD.H"
#include "dynamicFvMesh.H"
#include "singlePhaseTransportModel.H"
#include "turbulentTransportModel.H"
#include "simpleControl.H"
#include "fvOptions.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

int main(int argc, char *argv[])
{
    argList::addNote
    (
        "Steady-state solver for incompressible, turbulent flow"
        " with DC corona discharge (ionic wind) coupling."
    );

    #include "postProcess.H"

    #include "addCheckCaseOptions.H"
    #include "setRootCaseLists.H"
    #include "createTime.H"
    #include "createDynamicFvMesh.H"
    #include "createControl.H"
    #include "createFields.H"
    #include "initContinuityErrs.H"

    turbulence->validate();

    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

    Info<< "\nStarting time loop\n" << endl;

    while (simple.loop())
    {
        Info<< "Time = " << runTime.timeName() << nl << endl;

        // Do any mesh changes
        mesh.controlledUpdate();

        if (mesh.changing())
        {
            MRF.update();
        }

        // --- Electrostatic corrector
        {
            #include "VEqn.H"
            #include "rhoqEqn.H"
        }

        // --- Pressure-velocity SIMPLE corrector
        {
            #include "UEqn.H"
            #include "pEqn.H"
        }

        laminarTransport.correct();
        turbulence->correct();

        runTime.write();

        runTime.printExecutionTime(Info);
    }

    Info<< "End\n" << endl;

    return 0;
}


// ************************************************************************* //
