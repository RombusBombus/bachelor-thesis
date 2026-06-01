from ase.io import read
from ase.calculators.vasp import Vasp
from ase.visualize import view
import os
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()  # Load environment variables from .env file

atoms = read("TaCuN2_unrelaxed.cif")
view(atoms)

encut_values = [100, 200, 300, 350, 400, 450, 500]

for encut in encut_values:
    calc = Vasp(
        xc="PBE",
        encut=encut,
        kpts=(4, 4, 4),
        ibrion=-1,
        kpar=8,
        ncore=8,
        ismear=0,
        sigma=0.03,
        ISYM=-1
    )
    atoms.calc = calc

    folder = Path("encut_convergence") / f"encut_{encut}"
    os.makedirs(folder, exist_ok=True)

    calc.write_input(atoms)

    # move the generated input files to the corresponding folder
    for filename in ["INCAR", "POSCAR", "POTCAR", "KPOINTS"]:
        os.rename(filename, folder / filename)


kpoints_values = [1, 2, 3, 4, 5, 6, 7, 8]

for kpoints in kpoints_values:
    calc = Vasp(
        xc="PBE",
        encut=300,
        # kspacing=0.25,
        kpts=(kpoints, kpoints, kpoints),
        ibrion=-1,
        kpar=8,
        ncore=8
    )
    atoms.calc = calc

    folder = Path("kpoints_convergence") / f"kpoints_{kpoints}"
    os.makedirs(folder, exist_ok=True)

    calc.write_input(atoms)

    # move the generated input files to the corresponding folder
    for filename in ["INCAR", "POSCAR", "POTCAR", "KPOINTS"]:
        os.rename(filename, folder / filename)