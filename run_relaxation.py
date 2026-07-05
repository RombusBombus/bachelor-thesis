import os
import subprocess
from pathlib import Path

if __name__ == "__main__":
    folder = Path("relaxation")

    print(f"Running VASP in {folder}...")
    print(folder.absolute())

    # Change to the folder and launch the job_submit.sh script, capturing stdout
    prev_cwd = Path.cwd()
    try:
        os.chdir(folder.absolute())

        # relaxation/ is one level below the repo root, so the job script
        # lives one directory up (../), unlike the convergence runs (../../).
        result = subprocess.run(["sbatch", "../job_submit_vasp.sh"], capture_output=True, text=True)
        # Print stdout and stderr (if any)
        if result.stdout:
            print(result.stdout.strip())
        if result.stderr:
            print(result.stderr.strip())
    finally:
        os.chdir(prev_cwd)  # Change back to the original directory
