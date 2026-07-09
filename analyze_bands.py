#!/usr/bin/env python3
r"""Plot the TaCuN2 band structure along Gamma->M and A->L.

Reads ``vasprun.xml`` + ``KPOINTS`` from the finished non-self-consistent band
run (line-mode, ICHARG = 11) and writes a single figure with one panel per
segment, sharing the energy axis.  The two requested segments are
*discontinuous* in the Brillouin zone, so they are drawn as separate panels
(never joined by a connecting line).

Energies are referenced to the valence-band maximum (VBM -> 0) for a
semiconductor; for a metal they are referenced to the Fermi level instead.  The
line-mode Fermi level is not used as the zero because occupations cannot be
integrated from k-points that lie only on a path.

Usage
-----
    python analyze_bands.py [BANDS_DIR] [-o OUTDIR] [--emin -6] [--emax 6]

``BANDS_DIR`` defaults to ``nscf-bands``; the PDF goes to ``OUTDIR``
(default ``BANDS_DIR``).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: just write files
import matplotlib.pyplot as plt
import numpy as np
from pymatgen.electronic_structure.core import Spin
from pymatgen.io.vasp.outputs import BSVasprun

# ---------------------------------------------------------------------------
# Style (matches analyze_dos.py)
# ---------------------------------------------------------------------------
BAND_COLOR = "#2a78d6"   # valence/conduction bands
ZERO_LINE = "#52514e"    # VBM / Fermi reference
GAP_FILL = "#eda100"     # shaded band gap

plt.rcParams.update(
    {
        "font.family": "serif",  # use serif/main font for text elements
        "text.usetex": True,  # use inline math for ticks
        "pgf.rcfonts": False,  # don't setup fonts from rc parameters
        "axes.labelsize": 14,  # axis labels
        "legend.fontsize": 12,  # legend
        "xtick.labelsize": 12,  # x tick labels
        "ytick.labelsize": 12,  # y tick labels
    }
)

# Pretty labels for the high-symmetry points read from KPOINTS
POINT_LABELS = {
    "G": r"$\Gamma$",
    "GAMMA": r"$\Gamma$",
    "\\GAMMA": r"$\Gamma$",
    "M": r"$M$",
    "A": r"$A$",
    "L": r"$L$",
}


def _label(token):
    return POINT_LABELS.get(token.upper(), f"${token}$")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument(
        "bands_dir",
        nargs="?",
        default="nscf-bands",
        type=Path,
        help="directory with vasprun.xml and KPOINTS (default: nscf-bands)",
    )
    p.add_argument(
        "-o", "--outdir", type=Path, default=None,
        help="output directory for the PDF (default: BANDS_DIR)",
    )
    p.add_argument("--emin", type=float, default=-6.0, help="energy window min (eV)")
    p.add_argument("--emax", type=float, default=6.0, help="energy window max (eV)")
    args = p.parse_args()

    outdir = args.outdir or args.bands_dir
    outdir.mkdir(parents=True, exist_ok=True)

    bsv = BSVasprun(str(args.bands_dir / "vasprun.xml"))
    bs = bsv.get_band_structure(
        kpoints_filename=str(args.bands_dir / "KPOINTS"), line_mode=True
    )

    metal = bs.is_metal()
    if metal:
        zero = bs.efermi
        ylabel = r"$E - E_\mathrm{F}$ (eV)"
        cbm = None
    else:
        zero = bs.get_vbm()["energy"]
        cbm = bs.get_cbm()["energy"]
        ylabel = r"$E - E_\mathrm{VBM}$ (eV)"

    gap = bs.get_band_gap()
    print(f"E_Fermi (run)  = {bs.efermi:.3f} eV")
    print(f"metal          = {metal}")
    if not metal:
        print(f"VBM            = {bs.get_vbm()['energy']:.3f} eV")
        print(f"CBM            = {cbm:.3f} eV")
        print(f"band gap       = {gap['energy']:.3f} eV "
              f"({'direct' if gap['direct'] else 'indirect'}, {gap['transition']})")

    rec = bs.lattice_rec  # reciprocal lattice (2 pi / Angstrom)
    kpts = [k.frac_coords for k in bs.kpoints]

    # ------------------------------------------------------------------
    # Per-branch geometry: cumulative distance + reciprocal-space length
    # ------------------------------------------------------------------
    branches = []
    for br in bs.branches:
        i0, i1 = br["start_index"], br["end_index"]
        cart = np.array([rec.get_cartesian_coords(kpts[i]) for i in range(i0, i1 + 1)])
        seg = np.linalg.norm(np.diff(cart, axis=0), axis=1)
        dist = np.concatenate([[0.0], np.cumsum(seg)])
        start, end = [t.strip() for t in br["name"].split("-")]
        branches.append(
            dict(i0=i0, i1=i1, dist=dist, length=dist[-1], start=start, end=end)
        )

    # ------------------------------------------------------------------
    # Figure: one panel per branch, widths proportional to path length
    # ------------------------------------------------------------------
    fig, axes = plt.subplots(
        1, len(branches), sharey=True, figsize=(7.0, 4.6),
        gridspec_kw={"width_ratios": [b["length"] for b in branches], "wspace": 0.06},
    )
    if len(branches) == 1:
        axes = [axes]

    for ax, br in zip(axes, branches):
        sl = slice(br["i0"], br["i1"] + 1)
        d = br["dist"]
        for spin, bands in bs.bands.items():
            for band in bands[:, sl]:
                ax.plot(d, band - zero, color=BAND_COLOR, lw=1.1)

        # reference line (VBM or E_F) and shaded gap
        ax.axhline(0.0, color=ZERO_LINE, lw=1.0, ls="--")
        if not metal:
            ax.axhspan(0.0, cbm - zero, color=GAP_FILL, alpha=0.12, lw=0)

        ax.set_xlim(d[0], d[-1])
        ax.set_xticks([d[0], d[-1]])
        ax.set_xticklabels([_label(br["start"]), _label(br["end"])])
        ax.grid(axis="y")

    axes[0].set_ylim(args.emin, args.emax)
    axes[0].set_ylabel(ylabel)

    # mark the valence band maximum and the conduction band minimum
    # with two colored dots
    if not metal:
        vbm_kpt = bs.get_vbm()["kpoint"].frac_coords
        cbm_kpt = bs.get_cbm()["kpoint"].frac_coords
        for ax, br in zip(axes, branches):
            d = br["dist"]
            k0, k1 = kpts[br["i0"]], kpts[br["i1"]]
            if np.allclose(vbm_kpt, k0) or np.allclose(vbm_kpt, k1):
                ax.plot(d[0] if np.allclose(vbm_kpt, k0) else d[-1], 0.0,
                        "o", color=GAP_FILL, ms=10)
            if np.allclose(cbm_kpt, k0) or np.allclose(cbm_kpt, k1):
                ax.plot(d[0] if np.allclose(cbm_kpt, k0) else d[-1], cbm - zero,
                        "o", color=GAP_FILL, ms=10)

    outfile = outdir / "band_structure.pdf"
    fig.savefig(outfile, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {outfile}")


if __name__ == "__main__":
    main()
