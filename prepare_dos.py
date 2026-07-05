import shutil
from pathlib import Path

# ==========================================
# Einstellungen
# ==========================================

# Quelle: die abgeschlossene Relaxation (liefert Geometrie, POTCAR, CHGCAR)
source_dir = Path("relaxation")

# Zielverzeichnis fuer die DOS-Rechnung
directory = Path("dos")

# Dichtes, Gamma-zentriertes k-Netz fuer die DOS.
# Anisotrop wie bei der Relaxation (c ~ 5.6x a), aber deutlich feiner.
kmesh = (15, 15, 3)

# Energieaufloesung der DOS
NEDOS = 3001

# Plane-wave cutoff (konsistent mit Relaxation)
ENCUT = 520

# ==========================================
# Zielverzeichnis anlegen
# ==========================================

directory.mkdir(exist_ok=True)

# ==========================================
# Geometrie: relaxierte CONTCAR -> POSCAR
# (verbatim kopieren, damit die Atom-Reihenfolge exakt zum POTCAR passt)
# ==========================================

shutil.copy(source_dir / "CONTCAR", directory / "POSCAR")

# ==========================================
# POTCAR und CHGCAR aus der Relaxation uebernehmen
# CHGCAR wird fuer die nicht-selbstkonsistente Rechnung (ICHARG = 11) benoetigt.
# ==========================================

shutil.copy(source_dir / "POTCAR", directory / "POTCAR")
shutil.copy(source_dir / "CHGCAR", directory / "CHGCAR")

# ==========================================
# KPOINTS schreiben (automatisches Gamma-zentriertes Netz)
# ==========================================

with open(directory / "KPOINTS", "w") as f:
    f.write("Automatic dense mesh for DOS\n")
    f.write("0\n")
    f.write("Gamma\n")
    f.write(f"{kmesh[0]} {kmesh[1]} {kmesh[2]}\n")
    f.write("0 0 0\n")

# ==========================================
# INCAR schreiben
# ==========================================
# ICHARG = 11 : nicht-selbstkonsistent, liest die feste Ladungsdichte (CHGCAR)
# ISMEAR = -5 : Tetraeder-Methode mit Bloechl-Korrektur -> genaue DOS
# LORBIT = 11 : site- und l-projizierte (orbitalaufgeloeste) DOS in DOSCAR/PROCAR
# LREAL = .FALSE. : reziproke Projektoren (genau, kleine Zelle)

incar = f"""
SYSTEM = TaCuN2 DOS

ICHARG = 11
LORBIT = 11
NEDOS = {NEDOS}

ENCUT = {ENCUT}
PREC = Accurate
LREAL = .FALSE.

ISMEAR = -5

IBRION = -1
NSW = 0

LWAVE = .FALSE.
LCHARG = .FALSE.

NELM = 200
"""

with open(directory / "INCAR", "w") as f:
    f.write(incar.strip() + "\n")

print(f"DOS-Eingabedateien wurden in {directory}/ erstellt.")
