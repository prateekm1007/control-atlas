from pathlib import Path
from openmm.app import *
from openmm import *
from openmm.unit import *

def run_production_md(
    pdb: Path,
    output_dir: Path,
    ns: int,
    implicit_solvent="OBC2",
    platform="OpenCL"
):
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"🧪 Loading PDB: {pdb}")
    pdbfile = PDBFile(str(pdb))

    print("⚙️ Building forcefield")
    forcefield = ForceField('amber14-all.xml', 'amber14/tip3p.xml')

    if implicit_solvent == "OBC2":
        system = forcefield.createSystem(
            pdbfile.topology,
            nonbondedMethod=NoCutoff,
            constraints=HBonds,
            implicitSolvent=OBC2
        )
    else:
        raise ValueError("Unsupported solvent model")

    integrator = LangevinIntegrator(
        300*kelvin,
        1/picosecond,
        2*femtoseconds
    )

    platform_obj = Platform.getPlatformByName(platform)
    simulation = Simulation(pdbfile.topology, system, integrator, platform_obj)
    simulation.context.setPositions(pdbfile.positions)

    print("🔧 Minimizing energy")
    simulation.minimizeEnergy()

    print("🚀 Running production MD")
    steps = int(ns * 500_000)  # 2 fs timestep → 500k steps per ns

    simulation.reporters.append(
        StateDataReporter(
            str(output_dir / "log.txt"),
            1000,
            step=True,
            potentialEnergy=True,
            temperature=True,
            rmsd=True
        )
    )

    simulation.reporters.append(
        DCDReporter(str(output_dir / "trajectory.dcd"), 5000)
    )

    simulation.step(steps)

    print("✅ Tier-3 MD complete")
