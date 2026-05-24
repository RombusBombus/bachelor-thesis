import os
from pathlib import Path


if __name__ == "__main__":
    folder = Path("encut_convergence")
    subfolders = [f for f in folder.iterdir() if f.is_dir()]

    for subfolder in subfolders:
        print(f"Running VASP in {subfolder}...")
        os.system("job_submit.sh " + str(subfolder))