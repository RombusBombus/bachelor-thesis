from ase.io import read
from ase.calculators.vasp import Vasp
from dotenv import load_dotenv

load_dotenv()  # .env-Datei laden, um Umgebungsvariablen zu setzen (VASP_PP_PATH)

# ===== Parameter (auf das System TaCuN2 abgestimmt) =====
# Ebenenzahl / ENCUT:
# Haertester POTCAR ist N mit ENMAX = 400 eV. Fuer eine Volumenrelaxation
# (ISIF = 3) sollte ENCUT ~ 1.3 x ENMAX gewaehlt werden, um den Pulay-Stress
# klein zu halten -> 1.3 * 400 = 520 eV.
ENCUT = 520

# k-Punkte: Die Zelle ist stark anisotrop (a = b = 3.15 A, c = 17.54 A).
# Reziprok ist die c-Achse ~6x kuerzer als a/b, daher ein anisotropes,
# Gamma-zentriertes Netz (Gamma-zentriert ist fuer hexagonale Symmetrie noetig).
KPOINTS_MESH = (9, 9, 9)

# Relaxationsparameter
ISIF = 3          # relaxiere Ionen, Zellform und Volumen
EDIFF = 1e-6      # Energiekonvergenz SCF (eV)
EDIFFG = -0.01    # Kraftkonvergenz (eV/A)
NSW = 100         # maximale Ionen-Schritte
IBRION = 2        # konjugierter Gradient
ISMEAR = 0        # Gaussian-Verschmierung (Halbleiter/isolierend)
SIGMA = 0.05      # Verbreiterung (eV)
PREC = "Accurate" # Genauigkeitsstufe
LREAL = False     # reziproke Projektion (genau, kleine Zelle mit 12 Atomen)
XC = 'PBE'        # Austausch-Korrelationsfunktional

# Parallelisierung (an die verwendete Maschine anpassen)
KPAR = 8          # k-Punkt-Parallelisierung
NCORE = 8         # Kerne pro Band

# ===== Dateien schreiben =====
# 1. Struktur einlesen
atoms = read("TaCuN2_unrelaxed.cif")

# 2. VASP-Kalkulator konfigurieren
calc = Vasp(
    encut=ENCUT,
    xc=XC,
    kpts=KPOINTS_MESH,          # ASE erzeugt daraus eine KPOINTS-Datei
    gamma=True,                 # Gamma-zentriertes Netz
    isif=ISIF,
    ediff=EDIFF,
    ediffg=EDIFFG,
    nsw=NSW,
    ibrion=IBRION,
    ismear=ISMEAR,
    sigma=SIGMA,
    prec=PREC,
    lreal=LREAL,
    kpar=KPAR,
    ncore=NCORE,
    lwave=True,                 # WAVECAR schreiben (fuer Restart aus CONTCAR)
    lcharg=True,                # CHGCAR schreiben
    directory='relaxation999',     # Eingabedateien nach relaxation/ schreiben
)

# 3. Alle Eingabedateien erzeugen (INCAR, KPOINTS, POSCAR, POTCAR)
calc.write_input(atoms)

print("Alle Eingabedateien für die Relaxation wurden in relaxation/ erstellt.")
