"""Prepare a non-self-consistent band-structure calculation for TaCuN2.

The paths requested for comparison with the literature are

    Gamma -> M   and   A -> L

These are high-symmetry points of the HEXAGONAL Brillouin zone.  TaCuN2 has
space group R-3m (rhombohedral, R-centred) but is stored in the hexagonal
setting (a = b, gamma = 120 deg), so ASE detects a HEX lattice and the labels
Gamma/M/A/L map directly onto the reciprocal lattice of the CONTCAR.  We define
the points explicitly and assert they agree with ASE's detected special points,
so an unexpected cell (e.g. a primitive rhombohedral one, whose zone has no
M/A/L) fails loudly instead of producing a wrong path.

Note: the hexagonal cell is R-centred, hence non-primitive (3 formula units),
so the bands are folded relative to the primitive rhombohedral cell.  This is
fine for comparison as long as the reference used the same hexagonal cell.
"""

import shutil
from pathlib import Path

import numpy as np
from ase.io import read

# ==========================================
# Einstellungen
# ==========================================

source_dir = Path("relaxation")   # liefert Geometrie, POTCAR und CHGCAR
directory = Path("nscf-bands")

# Hochsymmetriepunkte der hexagonalen BZ (fraktionale reziproke Koordinaten)
HEX_POINTS = {
    "G": (0.0, 0.0, 0.0),   # Gamma
    "M": (0.5, 0.0, 0.0),
    "A": (0.0, 0.0, 0.5),
    "L": (0.5, 0.0, 0.5),
}

# Gewuenschte Pfade (getrennte Segmente)
SEGMENTS = [("G", "M"), ("A", "L")]
LABELS = {"G": r"\Gamma", "M": "M", "A": "A", "L": "L"}

# Punkte pro Segment
NPOINTS = 60

ENCUT = 520

# ==========================================
# Struktur einlesen und Zelle pruefen
# ==========================================

atoms = read(source_dir / "CONTCAR")
lat = atoms.cell.get_bravais_lattice()

print(f"Detected Bravais lattice: {lat}")
if lat.name != "HEX":
    raise SystemExit(
        f"Expected a HEX cell for the Gamma/M/A/L labels, got {lat.name}. "
        "The k-point coordinates below are only valid for the hexagonal setting."
    )

# Sanity-Check: unsere Koordinaten muessen mit ASEs Spezialpunkten uebereinstimmen.
ase_pts = atoms.cell.bandpath().special_points
for name, coord in HEX_POINTS.items():
    ref = ase_pts[name]
    if not np.allclose(coord, ref, atol=1e-6):
        raise SystemExit(
            f"Point {name}={coord} disagrees with ASE {name}={tuple(ref)} — "
            "check the cell setting."
        )
print("High-symmetry points verified against ASE special points.")

# ==========================================
# Zielverzeichnis anlegen und Dateien uebernehmen
# ==========================================

directory.mkdir(exist_ok=True)

# Geometrie verbatim kopieren (Atom-Reihenfolge passt zum POTCAR)
shutil.copy(source_dir / "CONTCAR", directory / "POSCAR")
# POTCAR und CHGCAR fuer die nicht-selbstkonsistente Rechnung (ICHARG = 11)
shutil.copy(source_dir / "POTCAR", directory / "POTCAR")
shutil.copy(source_dir / "CHGCAR", directory / "CHGCAR")

# ==========================================
# KPOINTS im Line-Mode schreiben
# ==========================================

path_desc = " ; ".join(f"{a}-{b}" for a, b in SEGMENTS)
lines = [
    f"Band structure path: {path_desc}",
    f"{NPOINTS}",
    "Line-mode",
    "Reciprocal",
]
for a, b in SEGMENTS:
    ka, kb = HEX_POINTS[a], HEX_POINTS[b]
    lines.append(f"{ka[0]:10.6f} {ka[1]:10.6f} {ka[2]:10.6f}  ! {a}")
    lines.append(f"{kb[0]:10.6f} {kb[1]:10.6f} {kb[2]:10.6f}  ! {b}")
    lines.append("")  # Leerzeile trennt die Segmente

with open(directory / "KPOINTS", "w") as f:
    f.write("\n".join(lines).rstrip() + "\n")

# ==========================================
# INCAR schreiben
# ==========================================
# ICHARG = 11 : nicht-selbstkonsistent, feste Ladungsdichte (CHGCAR) einlesen
# ISMEAR = 0  : Gauss-Verschmierung (Tetraeder braucht ein regulaeres Netz und
#               ist fuer einen Line-Mode-Pfad ungeeignet)
# LORBIT = 11 : orbitalprojizierte Beitraege (fat bands) in PROCAR

incar = f"""
SYSTEM = TaCuN2 band structure

ICHARG = 11
LORBIT = 11

ENCUT = {ENCUT}
PREC = Accurate
LREAL = .FALSE.

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

print(f"\nBand-structure inputs written to {directory}/")
print(f"  path: {path_desc}  ({NPOINTS} points per segment)")
for name in HEX_POINTS:
    print(f"  {LABELS[name]:>7} = {HEX_POINTS[name]}")
