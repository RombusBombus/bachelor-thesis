from ase.io import read
from ase.calculators.vasp import Vasp
from dotenv import load_dotenv

load_dotenv()  # .env-Datei laden, um Umgebungsvariablen zu setzen

# ===== Benutzereingaben (bitte an deine Werte anpassen) =====
ENCUT = 800                     # aus deinem ENCUT-Test (eV)
KPOINTS_MESH = (11, 11, 11)    # aus deinem KPOINTS-Test (Monkhorst-Pack, gamma-zentriert)

# Optionale Relaxationsparameter (können auch so bleiben)
ISIF = 3          # relaxiere Zellform und Volumen
EDIFF = 1e-6      # Energiekonvergenz (eV)
EDIFFG = -0.02    # Kraftkonvergenz (eV/Å)
NSW = 100         # maximale Ionen-Schritte
IBRION = 2        # konjugierter Gradient
ISMEAR = 0        # Gaussian-Besetzung (für Metalle/Halbleiter)
SIGMA = 0.05      # Verbreiterung (eV)
PREC = "Accurate" # Genauigkeitsstufe
XC = 'PBE'        # Austausch-Korrelationsfunktional

# ===== Dateien schreiben =====
# 1. POSCAR einlesen (muss im aktuellen Ordner existieren)
atoms = read("TaCuN2_unrelaxed.cif")

# 2. VASP-Kalkulator konfigurieren
calc = Vasp(
    encut=ENCUT,
    xc=XC,
    kpts=KPOINTS_MESH,          # ASE erzeugt daraus eine KPOINTS-Datei
    isif=ISIF,
    ediff=EDIFF,
    ediffg=EDIFFG,
    nsw=NSW,
    ibrion=IBRION,
    ismear=ISMEAR,
    sigma=SIGMA,
    prec=PREC,
    lwave=False,                # keine WAVE-Datei nach Relaxation
    lcharg=False,               # keine CHGCAR-Datei
    directory='.',              # schreibe Dateien in aktuelles Verzeichnis
    # Optional: Wenn deine POTCARs anders organisiert sind, kannst du
    # setup_paths = {'Element': '/pfad/zur/POTCAR'} nutzen.
)

# 3. Alle Eingabedateien erzeugen (INCAR, KPOINTS, POSCAR, POTCAR)
calc.write_input(atoms)

print("VASP-Eingabedateien wurden erfolgreich erstellt (INCAR, KPOINTS, POSCAR, POTCAR).")

# bewege dateien in relaxationsordner
import shutil
import os

if not os.path.exists('relaxation'):
    os.makedirs('relaxation')
shutil.move('INCAR', 'relaxation/INCAR')
shutil.move('KPOINTS', 'relaxation/KPOINTS')
shutil.move('POSCAR', 'relaxation/POSCAR')
shutil.move('POTCAR', 'relaxation/POTCAR')


print("Starte nun die Relaxation mit deinem VASP-Jobskript.")