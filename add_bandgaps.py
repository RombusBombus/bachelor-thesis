from pathlib import Path
import subprocess
from tqdm import tqdm


def main() -> None:
	base_dir = Path("cluster_results")
	snapshot_dirs = sorted(base_dir.glob("flow-otter-CuTaN2-5T/temperature_*/2-DFT/config_*"))
	for snapshot_dir in tqdm(snapshot_dirs):
		if not snapshot_dir.is_dir():
			continue

		output_file = snapshot_dir / "bandgap.log"
		# check if snapshot_dir contains EIGENVAL file
		if not (snapshot_dir / "EIGENVAL").is_file():
			print(f"Skipping {snapshot_dir} because EIGENVAL file is missing.")
			continue

		# skip if output_file already exists
		if output_file.is_file():
			print(f"Skipping {snapshot_dir} because bandgap.log already exists.")
			continue

		print(snapshot_dir)

		with output_file.open("w") as f:
			subprocess.run(
				[
					"vamp",
					"eigenval",
					"read",
					"--par",
					"bandgap",
				],
				cwd=snapshot_dir,
				stdout=f,
				stderr=subprocess.STDOUT,
				check=True,
			)


if __name__ == "__main__":
	main()
