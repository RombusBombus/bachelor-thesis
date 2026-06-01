import os
from pathlib import Path

if __name__ == "__main__":
    folder = Path("encut_convergence")
    subfolders = [f for f in folder.iterdir() if f.is_dir()]

    for subfolder in subfolders:
        print(f"Running VASP in {subfolder}...")

        print(subfolder.absolute())

        # Change to the subfolder and launch the job_submit.sh script
        os.chdir(subfolder.absolute())
        os.system("sbatch ../../job_submit_vasp.sh")
        os.chdir("../../")  # Change back to the original directory
