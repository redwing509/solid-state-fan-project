    // Space charge transport (steady, drift + convection + diffusion):
    //     div((U + muq*E)*rhoq) - laplacian(Dq, rhoq) == 0

    // face flux of ion drift, muq*E & Sf
    rhoqFlux = -muq*mesh.magSf()*fvc::snGrad(V);

    fvScalarMatrix rhoqEqn
    (
        fvm::div(phi + rhoqFlux, rhoq)
      - fvm::laplacian(Dq, rhoq)
    );

    rhoqEqn.relax();
    rhoqEqn.solve();

    // --- Diagnostics: electric current and max |E| on each boundary patch
    {
        // conduction + convection + diffusion current through faces [A]
        surfaceScalarField Jq
        (
            "Jq",
            fvc::interpolate(rhoq)*(phi + rhoqFlux)
          - Dq*mesh.magSf()*fvc::snGrad(rhoq)
        );

        forAll(mesh.boundary(), patchi)
        {
            const fvPatch& curPatch = mesh.boundary()[patchi];

            if (curPatch.coupled())
            {
                continue;
            }

            const label nFaces =
                returnReduce(curPatch.size(), sumOp<label>());

            if (nFaces == 0)
            {
                continue;
            }

            const scalar Ipatch = gSum(Jq.boundaryField()[patchi]);

            const scalarField magEp(mag(E.boundaryField()[patchi]));
            const scalar Emax =
                returnReduce
                (
                    magEp.size() ? max(magEp) : scalar(0),
                    maxOp<scalar>()
                );

            Info<< "patch " << curPatch.name()
                << ": I = " << Ipatch << " A"
                << ", max|E| = " << Emax << " V/m" << endl;
        }
    }
