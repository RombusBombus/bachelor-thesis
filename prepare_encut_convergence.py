from ase.io import read
from ase.calculators.vasp import Vasp
from ase.visualize import view
import os
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()  # Load environment variables from .env file

atoms = read("TaCuN2_unrelaxed.cif")
view(atoms)

encut_values = [300, 350, 400, 450, 500, 600, 700, 800]

for encut in encut_values:
    calc = Vasp(
        xc="PBE",
        encut=encut,
        # kspacing=0.25,
        kpts=(4, 4, 4),
        ibrion=-1,
    )
    atoms.calc = calc

    folder = Path("encut_convergence") / f"encut_{encut}"
    os.makedirs(folder, exist_ok=True)

    calc.write_input(atoms)

    # move the generated input files to the corresponding folder
    for filename in ["INCAR", "POSCAR", "POTCAR", "KPOINTS"]:
        os.rename(filename, folder / filename)
