from ase.io import read
from ase.calculators.vasp import Vasp
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()  # Load environment variables from .env file

atoms = read("CuTaN2_Test/TaCuN2_unrelaxed.cif")

# FIXED from ENCUT convergence
encut = 550

kpoint_list = [
    (4,4,2),
    (6,6,3),
    (8,8,4),
    (10,10,5)
]

results = []

for kpts in kpoint_list:

    folder = f"CuTaN2_Test/KPTS_{kpts[0]}x{kpts[1]}x{kpts[2]}"
    os.makedirs(folder, exist_ok=True)

    calc = Vasp(
        xc='PBE',
        encut=encut,

        kpts=kpts,

        nsw=0,
        ibrion=-1,

        ismear=0,
        sigma=0.05,

        ediff=1e-6,

        prec='Accurate',
        algo='Normal',
        lreal=False,

        directory=folder
    )

    atoms.calc = calc
    energy = atoms.get_potential_energy()

    results.append((kpts, energy))

    print(f"KPTS {kpts} -> Energy = {energy} eV")

with open("kpoints_convergence.dat", "w") as f:
    for kpts, energy in results:
        f.write(f"{kpts[0]} {kpts[1]} {kpts[2]} {energy}\n")