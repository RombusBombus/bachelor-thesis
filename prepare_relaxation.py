from ase.io import read
from ase.calculators.vasp import Vasp
from dotenv import load_dotenv

load_dotenv()  # .env-Datei laden, um Umgebungsvariablen zu setzen

# ===== Benutzereingaben (bitte an deine Werte anpassen) =====
ENCUT = 400                     # aus deinem ENCUT-Test (eV)
KPOINTS_MESH = (8, 8, 8)       # aus deinem KPOINTS-Test (Monkhorst-Pack, gamma-zentriert)

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

# Parallelisierung (1 Knoten = 72 Kerne auf Fritz)
KPAR = 6          # k-Punkt-Parallelisierung (72 = 6 x 12 Ranks)
NCORE = 4         # Kerne pro Band (12 / 4 = 3 Band-Gruppen)

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
    kpar=KPAR,
    ncore=NCORE,
    lwave=True,                # keine WAVE-Datei nach Relaxation
    lcharg=True,               # keine CHGCAR-Datei
    directory='relaxation',              # schreibe Dateien in aktuelles Verzeichnis
    # Optional: Wenn deine POTCARs anders organisiert sind, kannst du
    # setup_paths = {'Element': '/pfad/zur/POTCAR'} nutzen.
)

# 3. Alle Eingabedateien erzeugen (INCAR, KPOINTS, POSCAR, POTCAR)
calc.write_input(atoms)

print("Alle Eingabedateien für die Relaxation wurden erstellt.")