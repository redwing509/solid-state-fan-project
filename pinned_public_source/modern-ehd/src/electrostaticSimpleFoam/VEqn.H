    // Electric potential (Poisson equation):
    //     laplacian(V) == -rhoq/epsilon0

    while (simple.correctNonOrthogonal())
    {
        fvScalarMatrix VEqn
        (
            fvm::laplacian(V) == -rhoq/epsilon0
        );

        VEqn.solve();
    }

    // electric field from the potential
    E = -fvc::grad(V);
