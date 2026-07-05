import os
from pathlib import Path

if __name__ == "__main__":
    folder = Path("kpoints_convergence")
    subfolders = [f for f in folder.iterdir() if f.is_dir()]

    for subfolder in subfolders:
        print(f"Running VASP in {subfolder}...")

        print(subfolder.absolute())

        # Change to the subfolder and launch the job_submit.sh script, capturing stdout
        prev_cwd = Path.cwd()
        try:
            os.chdir(subfolder.absolute())
            import subprocess

            result = subprocess.run(["sbatch", "../../job_submit_vasp.sh"], capture_output=True, text=True)
            # Print stdout and stderr (if any)
            if result.stdout:
                print(result.stdout.strip())
            if result.stderr:
                print(result.stderr.strip())
        finally:
            os.chdir(prev_cwd)  # Change back to the original directory
