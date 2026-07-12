#!/usr/bin/env python3

import glob
import re
import csv


def parse_outcar(filename):
    """
    Extract energy(sigma->0) from a VASP OUTCAR file.
    Returns a list of energies, one per MD frame.
    """
    energies = []

    with open(filename, "r", errors="ignore") as f:
        for line in f:
            if "energy  without entropy" in line:
                match = re.search(r"energy\(sigma->0\)\s*=\s*([-+]?\d*\.\d+|\d+)", line)
                if match:
                    energies.append(float(match.group(1)))

    return energies


def main():
    for temperature in [300, 520, 650]:
        # Sort OUTCAR files by their numerical index (outcar_1, outcar_2, ..., outcar_10)
        outcar_files = sorted(
            glob.glob(f"/home/nico/MD_trajectories/{temperature}/outcar_*"),
            key=lambda x: int(re.search(r"(\d+)$", x).group(1))
        )
        # outcar_files = sorted(glob.glob(f"/home/nico/MD_trajectories/{temperature}/outcar_*"))

        if not outcar_files:
            raise FileNotFoundError("No files matching outcar_* found.")

        all_energies = []

        frame = 0
        for fname in outcar_files:
            print(f"Parsing {fname} ...")

            energies = parse_outcar(fname)

            for energy in energies:
                all_energies.append((frame, fname, energy))
                frame += 1

        print(f"Found {len(all_energies)} frames.")

        with open(f"energies_per_frame_{temperature}.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["frame", "source_file", "energy_eV"])

            writer.writerows(all_energies)

        print("Saved energies_per_frame.csv")


if __name__ == "__main__":
    main()