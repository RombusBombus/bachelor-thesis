"""Plot a publication-quality Brillouin zone figure for the crystal in a CIF file.

The structure in ``TaCuN2_unrelaxed.cif`` is rhombohedral (space group R-3m,
No. 166) supplied in the hexagonal setting.  The first Brillouin zone must
therefore be constructed from the *primitive* reciprocal lattice, not the
conventional hexagonal one.  We let pymatgen's ``HighSymmKpath`` (Setyawan-
Curtarolo convention) standardise the primitive cell so that the drawn zone,
the high-symmetry points and the recommended band-structure path are all
mutually consistent.

Output: ``brillouin_zone.pdf`` (vector, ready for a thesis).
"""

from __future__ import annotations

import numpy as np
import matplotlib
matplotlib.use("Agg")  # headless, vector-only output (no GUI backend)
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection

from pymatgen.core import Structure
from pymatgen.symmetry.bandstructure import HighSymmKpath

CIF_FILE = "TaCuN2_unrelaxed.cif"
OUT_PDF = "brillouin_zone.pdf"

# ---------------------------------------------------------------------------
# Colours / style
# ---------------------------------------------------------------------------
FACE_COLOR = "#4C72B0"      # BZ facet fill
EDGE_COLOR = "#2F4F6F"      # BZ facet edges
PATH_COLOR = "#C44E52"      # recommended k-path
PT_COLOR = "#C44E52"        # high-symmetry points
VEC_COLOR = "#55A868"       # reciprocal lattice vectors


def _format_formula(formula: str) -> str:
    """Render a chemical formula with mathtext subscripts, e.g. TaCuN2 -> TaCuN$_2$."""
    import re
    return re.sub(r"(\d+)", r"$_{\1}$", formula)


def latexify(label: str) -> str:
    """Turn a pymatgen k-point label such as ``\\Gamma`` or ``B_1`` into
    a matplotlib mathtext string."""
    return f"${label}$"


def main() -> None:
    structure = Structure.from_file(CIF_FILE)

    kpath = HighSymmKpath(structure)
    real_lat = kpath.prim.lattice               # real-space primitive lattice
    rec_lat = kpath.prim_rec                     # its reciprocal lattice
    kpoints = kpath.kpath["kpoints"]            # {label: frac coords}
    path = kpath.kpath["path"]                  # list of label sequences

    # First Brillouin zone = Wigner-Seitz cell of the reciprocal lattice.
    # pymatgen's helper builds it from the *real-space* lattice.
    bz_faces = real_lat.get_brillouin_zone()    # list of faces (arrays of verts)

    # ------------------------------------------------------------------
    # Figure
    # ------------------------------------------------------------------
    fig = plt.figure(figsize=(9.0, 4.8))
    ax = fig.add_subplot(111, projection="3d")

    # --- Brillouin zone facets -----------------------------------------
    poly = Poly3DCollection(
        bz_faces,
        facecolor=FACE_COLOR,
        edgecolor="none",
        alpha=0.12,
    )
    ax.add_collection3d(poly)

    # Draw edges separately so they stay crisp and are not washed out by alpha.
    edges = []
    for face in bz_faces:
        f = np.asarray(face)
        edges.extend([[f[i], f[(i + 1) % len(f)]] for i in range(len(f))])
    edge_lc = Line3DCollection(edges, colors=EDGE_COLOR, linewidths=1.2)
    ax.add_collection3d(edge_lc)

    # --- Recommended k-path --------------------------------------------
    path_segments = []
    for branch in path:
        for a, b in zip(branch[:-1], branch[1:]):
            path_segments.append(
                [rec_lat.get_cartesian_coords(kpoints[a]),
                 rec_lat.get_cartesian_coords(kpoints[b])]
            )
    path_lc = Line3DCollection(path_segments, colors=PATH_COLOR,
                               linewidths=2.0, zorder=5)
    ax.add_collection3d(path_lc)

    # --- High-symmetry points + labels ---------------------------------
    # Cartesian positions of every labelled point.
    coords = {lbl: rec_lat.get_cartesian_coords(f) for lbl, f in kpoints.items()}
    bz_reach = np.abs(np.vstack(bz_faces)).max()
    crop_pts3d = list(np.vstack(bz_faces))  # 3-D points to keep in frame
    for label, c in coords.items():
        ax.scatter(*c, color=PT_COLOR, s=34, depthshade=False,
                   edgecolor="white", linewidth=0.6, zorder=6)
        # Offset the label radially outward from the zone centre (Gamma) so
        # that clustered points stay legible.  Gamma itself is nudged up.
        r = np.linalg.norm(c)
        direction = c / r if r > 1e-6 else np.array([0.0, 0.0, 1.0])
        pos = c + direction * 0.18 * bz_reach
        # Thin leader line so an offset label is never ambiguous.
        ax.plot(*np.array([c, pos]).T, color="0.5", linewidth=0.5, zorder=6)
        ax.text(*pos, latexify(label), fontsize=12.5,
                ha="center", va="center", zorder=7)
        crop_pts3d.append(pos)

    # ------------------------------------------------------------------
    # Cosmetics: equal scale on every axis (so angles stay true) while
    # cropping the box tightly to the flat zone to avoid empty margins.
    # ------------------------------------------------------------------
    verts = np.vstack(bz_faces)
    lo, hi = verts.min(0), verts.max(0)
    pad = 0.30 * (hi - lo).max()          # room for the outward labels
    lo, hi = lo - pad, hi + pad
    ax.set_xlim(lo[0], hi[0])
    ax.set_ylim(lo[1], hi[1])
    ax.set_zlim(lo[2], hi[2])
    ax.set_box_aspect(hi - lo)            # equal unit length on all axes

    ax.set_axis_off()
    ax.view_init(elev=52, azim=-40)

    # Matplotlib's "tight" bbox for a 3-D axes reserves the full (mostly empty)
    # square projection region.  Crop instead to the drawn geometry: project
    # the 3-D points to display coordinates, then sit the title just above the
    # zone so there is no empty band between them.
    from matplotlib.transforms import Bbox
    from mpl_toolkits.mplot3d import proj3d
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    pts = np.asarray(crop_pts3d)
    xp, yp, _ = proj3d.proj_transform(pts[:, 0], pts[:, 1], pts[:, 2], ax.M)
    disp = ax.transData.transform(np.c_[xp, yp])
    zone = Bbox([[disp[:, 0].min(), disp[:, 1].min()],
                 [disp[:, 0].max(), disp[:, 1].max()]])

    formula = _format_formula(structure.composition.reduced_formula)
    title = fig.text(
        0.5, zone.ymax / fig.bbox.height + 0.02,
        f"First Brillouin zone of {formula}  (R$\\bar{{3}}$m, No. 166)",
        fontsize=14, ha="center", va="bottom", transform=fig.transFigure,
    )
    fig.canvas.draw()

    bb = Bbox.union([zone, title.get_window_extent(renderer)])
    bb = bb.expanded(1.04, 1.06).transformed(fig.dpi_scale_trans.inverted())

    fig.savefig(OUT_PDF, bbox_inches=bb, transparent=True)
    fig.savefig(OUT_PDF.replace(".pdf", ".png"), dpi=200, bbox_inches=bb)
    print(f"Saved {OUT_PDF}")
    print(f"High-symmetry points: {', '.join(kpoints)}")
    print(f"Path: {path}")


if __name__ == "__main__":
    main()
