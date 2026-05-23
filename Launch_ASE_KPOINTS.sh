#!/bin/bash
#SBATCH --job-name=encut_test
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00

# Umgebungsvariablen setzen
export OMP_NUM_THREADS=1
ulimit -s unlimited

# ASE-VASP Umgebungsvariablen (beachte: srun nicht vor python)
export ASE_VASP_COMMAND="srun vasp_std"
# ... (weitere Modul-Ladungen etc.) ...

# Python-Skript ausführen
python KPOINTS_convergence.py