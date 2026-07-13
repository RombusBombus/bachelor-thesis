
import numpy as np
import matplotlib.pyplot as plt
from pymatgen.io.vasp.outputs import Xdatcar
from pathlib import Path


# ===========================
# User parameters
# ===========================

XDATCAR_FILES = ["XDATCAR_300", "XDATCAR_520", "XDATCAR_650"]
SPECIES_PAIRS = [("Ta", "N"), ("Cu", "N")]
OUTPUT_DIR = Path("rdf_results")

R_MAX = 12.0          # Angstrom
DR = 0.02            # Bin width (Angstrom)

START_FRAME = 0      # Skip equilibration if desired
END_FRAME = None     # None = use all remaining frames


for XDATCAR_FILE in XDATCAR_FILES:
    for SPECIES1, SPECIES2 in SPECIES_PAIRS:

        print(f"Calculating RDF for {SPECIES1}-{SPECIES2} in {XDATCAR_FILE}...")

        # ===========================
        # Read trajectory and calculate RDF
        # ===========================

        output_path = OUTPUT_DIR / f"{XDATCAR_FILE}_{SPECIES1}-{SPECIES2}_RDF.dat"


        print("Reading trajectory...")
        xdat = Xdatcar(XDATCAR_FILE)
        structures = xdat.structures

        if END_FRAME is None:
            END_FRAME = len(structures)

        structures = structures[START_FRAME:END_FRAME]

        print(f"Using {len(structures)} frames.")

        nbins = int(R_MAX / DR)
        edges = np.linspace(0.0, R_MAX, nbins + 1)
        centers = 0.5 * (edges[:-1] + edges[1:])

        hist = np.zeros(nbins)

        total_frames = len(structures)

        for frame_number, structure in enumerate(structures, 1):

            lattice = structure.lattice
            volume = lattice.volume

            species = [site.specie.symbol for site in structure]

            ta_indices = [i for i, s in enumerate(species) if s == SPECIES1]
            n_indices = [i for i, s in enumerate(species) if s == SPECIES2]

            N_ta = len(ta_indices)
            N_n = len(n_indices)

            frac_coords = structure.frac_coords

            for i in ta_indices:
                fi = frac_coords[i]

                for j in n_indices:
                    fj = frac_coords[j]

                    # Fractional displacement
                    d = fj - fi

                    # Minimum-image convention
                    d -= np.round(d)

                    # Cartesian displacement
                    dcart = lattice.get_cartesian_coords(d)

                    r = np.linalg.norm(dcart)

                    if r < R_MAX:
                        bin_index = int(r / DR)
                        hist[bin_index] += 1

            if frame_number % 100 == 0:
                print(f"Processed {frame_number}/{total_frames} frames")

        print("Normalizing RDF...")

        # Average volume
        avg_volume = np.mean([s.lattice.volume for s in structures])

        rho_N = N_n / avg_volume

        g = np.zeros_like(hist)

        for k in range(nbins):

            r_inner = edges[k]
            r_outer = edges[k + 1]

            shell_volume = (4.0 / 3.0) * np.pi * (r_outer**3 - r_inner**3)

            expected = (
                N_ta *
                rho_N *
                shell_volume *
                total_frames
            )

            if expected > 0:
                g[k] = hist[k] / expected

        # Save RDF
        np.savetxt(
            output_path,
            np.column_stack((centers, g)),
            header="r(Angstrom)   g(r)"
        )

        print(f"Saved {output_path}")