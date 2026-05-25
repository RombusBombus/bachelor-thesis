from pathlib import Path

from ase.io import read, write
from ase.dft.kpoints import bandpath

# ==========================================
# Einstellungen
# ==========================================

structure_file = "CONTCAR"
directory = Path("bandstructure")

# Hochsymmetriepfad:
# Beispiele:
# "GXMGRX"
# "GXWKGLUWLK,UX"
path_string = "GXMG"

npoints = 100

# ==========================================
# Struktur einlesen
# ==========================================

atoms = read(structure_file)

# ==========================================
# Bandpfad erzeugen
# ==========================================

bp = atoms.cell.bandpath(path_string, npoints=npoints)

# ==========================================
# Verzeichnis anlegen
# ==========================================

directory.mkdir(exist_ok=True)

# ==========================================
# POSCAR schreiben
# ==========================================

write(directory / "POSCAR", atoms, format="vasp")

# ==========================================
# KPOINTS schreiben
# ==========================================

with open(directory / "KPOINTS", "w") as f:
    f.write("Bandstructure path\n")
    f.write(f"{len(bp.kpts)}\n")
    f.write("Reciprocal\n")

    for k in bp.kpts:
        f.write(f"{k[0]:12.8f} {k[1]:12.8f} {k[2]:12.8f} 1\n")

# ==========================================
# INCAR schreiben
# ==========================================

incar = """
SYSTEM = Bandstructure

ICHARG = 11
LORBIT = 11

ENCUT = 520
PREC = Accurate

ISMEAR = 0
SIGMA = 0.05

IBRION = -1
NSW = 0

LWAVE = .FALSE.
LCHARG = .FALSE.

NELM = 200
"""

with open(directory / "INCAR", "w") as f:
    f.write(incar.strip() + "\n")

