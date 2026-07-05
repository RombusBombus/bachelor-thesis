#!/usr/bin/env python3
"""Plot the orbital-resolved density of states of the TaCuN2 DOS run.

Reads ``vasprun.xml`` from a finished VASP DOS calculation (LORBIT = 11) and
writes three thesis-quality figures, all with the energy axis referenced to the
Fermi level (E - E_F, so E_F = 0):

    dos_total.pdf     total DOS (filled), Fermi level and band gap marked
    dos_element.pdf   site-projected DOS summed per element (Ta, Cu, N)
    dos_orbital.pdf   orbital-resolved (s/p/d) DOS, one panel per element

Usage
-----
    python analyze_dos.py [DOS_DIR] [-o OUTDIR] [--emin -8] [--emax 6]

``DOS_DIR`` defaults to ``dos``; figures go to ``OUTDIR`` (default ``DOS_DIR``).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: just write files
import matplotlib.pyplot as plt
import numpy as np
from pymatgen.electronic_structure.core import Spin
from pymatgen.io.vasp.outputs import Vasprun

# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------
# Colourblind-safe categorical palette (fixed order; validated dataviz theme).
PALETTE = ["#2a78d6", "#1baf7a", "#eda100", "#4a3aa7", "#e34948", "#eb6834"]
TOTAL_FILL = "#d9d8d4"
TOTAL_LINE = "#6f6e6a"
FERMI_LINE = "#52514e"

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

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _densities(dos):
    """Return (up, down_or_None) density arrays for a pymatgen Dos-like object."""
    up = dos.densities[Spin.up]
    down = dos.densities.get(Spin.down)  # None for a non-spin-polarised run
    return up, down


def _plot_series(ax, energy, dos, color, label, fill=True):
    """Plot one DOS series; mirror spin-down below the axis if present."""
    up, down = _densities(dos)
    ax.plot(energy, up, color=color, lw=1.6, label=label)
    if fill:
        ax.fill_between(energy, up, color=color, alpha=0.15)
    if down is not None:
        ax.plot(energy, -down, color=color, lw=1.6)
        if fill:
            ax.fill_between(energy, -down, color=color, alpha=0.15)


def _decorate(ax, emin, emax, spin_polarised, ymax=None):
    """Fermi line, limits, spine cleanup shared by every panel."""
    ax.axvline(0.0, color=FERMI_LINE, lw=1.0, ls="--")
    ax.set_xlim(emin, emax)
    if spin_polarised:
        lim = ymax if ymax is not None else max(abs(np.array(ax.get_ylim())))
        ax.set_ylim(-lim, lim)
        ax.axhline(0.0, color="#b7b6b2", lw=0.6)
    else:
        ax.set_ylim(0, ymax)
    # ax.spines[["top", "right"]].set_visible(False)


def _window_max(energy, dos_list, emin, emax):
    """Largest density within [emin, emax] across a list of Dos objects (headroom)."""
    mask = (energy >= emin) & (energy <= emax)
    peak = 0.0
    for dos in dos_list:
        for arr in _densities(dos):
            if arr is not None:
                peak = max(peak, float(np.max(arr[mask])))
    return peak * 1.08


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------
def plot_total(cdos, energy, emin, emax, spin, gap, outfile):
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    up, down = _densities(cdos)
    ax.plot(energy, up, color=TOTAL_LINE, lw=1.4)
    ax.fill_between(energy, up, color=TOTAL_FILL)
    if down is not None:
        ax.plot(energy, -down, color=TOTAL_LINE, lw=1.4)
        ax.fill_between(energy, -down, color=TOTAL_FILL)

    ymax = _window_max(energy, [cdos], emin, emax)
    _decorate(ax, emin, emax, spin, ymax)

    # Fermi label + gap annotation
    ax.text(
        0.0,
        ymax * 0.96,
        r"  $E_\mathrm{F}$",
        color=FERMI_LINE,
        va="top",
        ha="left",
        fontsize=9,
    )
    # if gap and gap > 0.01:
    #     ax.set_title(f"TaCuN$_2$ — total DOS (gap = {gap:.2f} eV)")
    # else:
    #     ax.set_title("TaCuN$_2$ — total DOS (metallic)")

    ax.set_xlabel(r"$E - E_\mathrm{F}$ (eV)")
    ax.set_ylabel("DOS (states / eV)")
    plt.grid()
    fig.tight_layout()
    fig.savefig(outfile)
    plt.close(fig)


def plot_element(cdos, energy, emin, emax, spin, outfile):
    el_dos = cdos.get_element_dos()  # {Element: Dos}
    # stable, readable order
    elements = sorted(el_dos, key=lambda e: e.symbol)

    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    for i, el in enumerate(elements):
        _plot_series(ax, energy, el_dos[el], PALETTE[i % len(PALETTE)], el.symbol)

    ymax = _window_max(energy, list(el_dos.values()), emin, emax)
    _decorate(ax, emin, emax, spin, ymax)
    # ax.set_title("TaCuN$_2$ — element-projected DOS")
    ax.set_xlabel(r"$E - E_\mathrm{F}$ (eV)")
    ax.set_ylabel("DOS (states / eV)")
    ax.legend(loc="upper right")
    plt.grid()
    fig.tight_layout()
    fig.savefig(outfile)
    plt.close(fig)


def plot_orbital(cdos, energy, emin, emax, spin, outfile):
    el_dos = cdos.get_element_dos()
    elements = sorted(el_dos, key=lambda e: e.symbol)
    n = len(elements)

    fig, axes = plt.subplots(n, 1, figsize=(7.0, 2.5 * n), sharex=True)
    if n == 1:
        axes = [axes]

    # consistent orbital -> colour mapping across all panels
    orb_color = {"s": PALETTE[0], "p": PALETTE[1], "d": PALETTE[2], "f": PALETTE[3]}

    for ax, el in zip(axes, elements):
        spd = cdos.get_element_spd_dos(el.symbol)  # {OrbitalType: Dos}
        # order s, p, d, f
        ordered = sorted(spd.items(), key=lambda kv: kv[0].value)
        for orb, dos in ordered:
            _plot_series(
                ax,
                energy,
                dos,
                orb_color.get(orb.name, "#888"),
                f"{el.symbol} {orb.name}",
            )
        ymax = _window_max(energy, [d for _, d in ordered], emin, emax)
        _decorate(ax, emin, emax, spin, ymax)
        ax.legend(loc="upper right", ncol=len(ordered))
        ax.set_ylabel("DOS\n(states / eV)")

    # axes[0].set_title("TaCuN$_2$ — orbital-resolved DOS")
    axes[-1].set_xlabel(r"$E - E_\mathrm{F}$ (eV)")
    plt.grid()
    fig.tight_layout()
    fig.savefig(outfile)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument(
        "dos_dir",
        nargs="?",
        default="dos",
        type=Path,
        help="directory with vasprun.xml (default: dos)",
    )
    p.add_argument(
        "-o",
        "--outdir",
        type=Path,
        default=None,
        help="output directory for the PDFs (default: DOS_DIR)",
    )
    p.add_argument("--emin", type=float, default=-8.0, help="energy window min (eV)")
    p.add_argument("--emax", type=float, default=6.0, help="energy window max (eV)")
    args = p.parse_args()

    outdir = args.outdir or args.dos_dir
    outdir.mkdir(parents=True, exist_ok=True)

    vasprun = Vasprun(
        str(args.dos_dir / "vasprun.xml"),
        parse_dos=True,
        parse_eigen=False,
        parse_projected_eigen=False,
    )
    cdos = vasprun.complete_dos
    energy = cdos.energies - cdos.efermi  # reference to Fermi level
    spin = Spin.down in cdos.densities
    gap = cdos.get_gap()

    print(f"E_Fermi = {cdos.efermi:.3f} eV")
    print(f"spin-polarised: {spin}")
    print(f"band gap = {gap:.3f} eV")

    plot_total(cdos, energy, args.emin, args.emax, spin, gap, outdir / "dos_total.pdf")
    plot_element(cdos, energy, args.emin, args.emax, spin, outdir / "dos_element.pdf")
    plot_orbital(cdos, energy, args.emin, args.emax, spin, outdir / "dos_orbital.pdf")

    print(f"Wrote dos_total.pdf, dos_element.pdf, dos_orbital.pdf to {outdir}/")


if __name__ == "__main__":
    main()
