    // Momentum predictor

    MRF.correctBoundaryVelocity(U);

    // EHD body force per unit mass: rhoq*E/rhoFluid [m/s^2]
    // (electricForceFactor is 1 or 0 according to the electricForce switch)
    tmp<fvVectorMatrix> tUEqn
    (
        fvm::div(phi, U)
      + MRF.DDt(U)
      + turbulence->divDevReff(U)
     ==
        fvOptions(U)
      + electricForceFactor*rhoq*E/rhoFluid
    );
    fvVectorMatrix& UEqn = tUEqn.ref();

    UEqn.relax();

    fvOptions.constrain(UEqn);

    if (simple.momentumPredictor())
    {
        solve(UEqn == -fvc::grad(p));

        fvOptions.correct(U);
    }
