Info<< "Reading field p\n" << endl;
volScalarField p
(
    IOobject
    (
        "p",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);

Info<< "Reading field U\n" << endl;
volVectorField U
(
    IOobject
    (
        "U",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);

#include "createPhi.H"


label pRefCell = 0;
scalar pRefValue = 0.0;
setRefCell(p, simple.dict(), pRefCell, pRefValue);
mesh.setFluxRequired(p.name());


singlePhaseTransportModel laminarTransport(U, phi);

autoPtr<incompressible::turbulenceModel> turbulence
(
    incompressible::turbulenceModel::New(U, phi, laminarTransport)
);

#include "createMRF.H"
#include "createFvOptions.H"


// * * * * * * * * * Electrostatics (electrostaticSimpleFoam) * * * * * * * //

Info<< "Reading electricProperties\n" << endl;

IOdictionary electricProperties
(
    IOobject
    (
        "electricProperties",
        runTime.constant(),
        mesh,
        IOobject::MUST_READ_IF_MODIFIED,
        IOobject::NO_WRITE
    )
);

// vacuum permittivity [A^2 s^4/(kg m^3)], e.g. 8.854e-12
dimensionedScalar epsilon0
(
    "epsilon0",
    dimensionSet(-1, -3, 4, 0, 0, 2, 0),
    electricProperties
);

// ion mobility [m^2/(V s)] = [A s^2/kg], e.g. 1.8e-4 for positive ions in air
dimensionedScalar muq
(
    "muq",
    dimensionSet(-1, 0, 2, 0, 0, 1, 0),
    electricProperties
);

// ion diffusivity [m^2/s]
dimensionedScalar Dq
(
    "Dq",
    dimensionSet(0, 2, -1, 0, 0, 0, 0),
    electricProperties
);

// fluid mass density [kg/m^3]; needed because p is kinematic pressure
dimensionedScalar rhoFluid
(
    "rhoFluid",
    dimensionSet(1, -3, 0, 0, 0, 0, 0),
    electricProperties
);

// switch for the EHD body force in the momentum equation:
// on  -> ionic wind acts on the flow
// off -> one-way: electrostatics computed but flow is not forced
Switch electricForce(electricProperties.get<Switch>("electricForce"));

// multiply the body force term by 1 or 0 according to the switch
dimensionedScalar electricForceFactor
(
    "electricForceFactor",
    dimless,
    electricForce ? 1.0 : 0.0
);

Info<< "Reading field V (electric potential)\n" << endl;
volScalarField V
(
    IOobject
    (
        "V",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);

Info<< "Reading field rhoq (space charge density)\n" << endl;
volScalarField rhoq
(
    IOobject
    (
        "rhoq",
        runTime.timeName(),
        mesh,
        IOobject::MUST_READ,
        IOobject::AUTO_WRITE
    ),
    mesh
);

Info<< "Calculating field E\n" << endl;
volVectorField E
(
    IOobject
    (
        "E",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::AUTO_WRITE
    ),
    -fvc::grad(V)
);

// face flux of charge due to ion drift, muq*E & Sf  [m^3/s]
surfaceScalarField rhoqFlux
(
    IOobject
    (
        "rhoqFlux",
        runTime.timeName(),
        mesh,
        IOobject::NO_READ,
        IOobject::NO_WRITE
    ),
    -muq*mesh.magSf()*fvc::snGrad(V)
);
