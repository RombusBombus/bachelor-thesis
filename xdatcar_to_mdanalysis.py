#!/usr/bin/env python3

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ase.io import read, write

import MDAnalysis as mda
from MDAnalysis.analysis import rms
from MDAnalysis.analysis.msd import EinsteinMSD

from pathlib import Path

# -----------------------------
# User settings
# -----------------------------

def analyze(temperature):

    xdatcar_file = f"XDATCAR_{temperature}"
    project_dir = Path(f"mdanalysis/{temperature}")
    project_dir.mkdir(parents=True, exist_ok=True)
    xyz_file = project_dir / "trajectory.xyz"

    # atom selection for analysis
    # examples:
    # "all"
    # "name H"
    # "index 0:100"
    selection = "all"


    # -----------------------------
    # Step 1: Convert XDATCAR -> XYZ
    # -----------------------------

    print("Reading XDATCAR...")

    trajectory = read(xdatcar_file, index=":")

    print(f"Number of frames: {len(trajectory)}")
    print(f"Number of atoms: {len(trajectory[0])}")


    print("Writing XYZ trajectory...")

    write(xyz_file, trajectory, format="extxyz")

    print(f"Written: {xyz_file}")


    # -----------------------------
    # Step 2: Load with MDAnalysis
    # -----------------------------

    print("Loading trajectory with MDAnalysis...")

    u = mda.Universe(xyz_file, format="XYZ")

    print(u)


    atoms = u.select_atoms(selection)

    print(f"Selected atoms: {len(atoms)}")


    # -----------------------------
    # Step 3: RMSD relative to first frame
    # -----------------------------

    print("Calculating RMSD...")

    rmsd = []

    reference = atoms.positions.copy()

    for ts in u.trajectory:

        displacement = atoms.positions - reference

        value = np.sqrt(np.mean(np.sum(displacement**2, axis=1)))

        rmsd.append(value)


    rmsd = np.array(rmsd)


    plt.figure(figsize=(7, 4))
    plt.plot(rmsd)

    plt.xlabel("MD step")
    plt.ylabel("RMSD (Å)")
    plt.tight_layout()

    plt.savefig(project_dir / "rmsd.png", dpi=300)

    print("Saved rmsd.png")


    # -----------------------------
    # Step 4: Mean squared displacement
    # -----------------------------

    print("Calculating MSD...")

    u = mda.Universe(xyz_file, format="XYZ")

    msd_analysis = EinsteinMSD(u, select=selection, msd_type="xyz", fft=True)

    msd_analysis.run()


    msd = msd_analysis.results.timeseries


    plt.figure(figsize=(7, 4))

    plt.plot(msd)

    plt.xlabel("Lag time")
    plt.ylabel("MSD (Å$^2$)")

    plt.tight_layout()

    plt.savefig(project_dir / "msd.png", dpi=300)

    # load the energies_per_frame_300.csv file
    energies_file = f"energies_per_frame_{temperature}.csv"

    # plot energy_eV
    
    df = pd.read_csv(energies_file)
    plt.figure(figsize=(7, 4))
    plt.plot(df["energy_eV"])
    plt.xlabel("Frame")
    plt.ylabel("Energy (eV)")
    plt.tight_layout()
    plt.savefig(project_dir / "energies.png", dpi=300)
    print("Saved energies.png")


    print("Analysis finished.")


if __name__ == "__main__":
    temperatures = [300, 520, 650]

    for temperature in temperatures:
        analyze(temperature)