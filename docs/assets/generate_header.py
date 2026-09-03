# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN MIF Liner Core — repository header artwork generator

"""Generate the three README header images (1280x640) for this repository.

Every image is original generated artwork derived from this repository's
own domain surface — the material liner closing on a premagnetised
target, the two implosion-velocity branches the configuration model
distinguishes, and the mechanical/liquid liner classes. The branch
artwork follows the cited assessment: the slow material-liner branch is
of order 10^2 m/s, contrasted with the 10^3-10^4 m/s fast metal-shell
branch. The right-hand text panel states only facts backed by the
repository itself.

Outputs (written next to this script):

- ``repo_header.png`` — the material liner closing on its
  premagnetised target (used by ``README.md``).
- ``repo_header_velocity_branches.png`` — the two velocity branches
  with the declared advisory bound.
- ``repo_header_liner_classes.png`` — mechanical shell beside liquid
  liner, both carrying a premagnetised target.

Generation-time tooling only: requires ``numpy`` and ``matplotlib``,
which are deliberately not part of the pinned development lock. Run as
``python3 docs/assets/generate_header.py`` from the repository root.
The output is deterministic (fixed geometry, no random input).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

OUT_DIR = Path(__file__).resolve().parent

BG = "#00050a"
CYAN = "#00ccff"
MAGENTA = "#ff00ff"
STEEL = "#334466"
PROBE = "#66aaff"
RED = "#ff3366"
GREEN = "#3ddc84"

WIDTH_IN, HEIGHT_IN, DPI = 12.8, 6.4, 100

TITLE_METRICS: list[tuple[str, str]] = [
    ("Device Configuration", "mechanical_or_liquid_liner_mif"),
    ("Hard Invariants", "liner class · target premagnetisation"),
    ("Velocity Bound", "slow branch: above 1 km/s flagged"),
    ("Reference", "LA-7686-MS (1979), Introduction"),
    ("Plan Envelope", "v1.1.0 · synthetic · review-only"),
    ("Quality Gates", "100% branch cov · mypy --strict"),
]


def _pyplot() -> Any:
    """Return pyplot configured for headless Agg rendering."""
    import matplotlib as mpl

    mpl.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def _glow_cmap() -> Any:
    """Build the family glow colormap (deep navy to cyan)."""
    from matplotlib.colors import LinearSegmentedColormap

    return LinearSegmentedColormap.from_list(
        "scpn_glow",
        ["#00050a", "#001428", "#002d55", "#005588", "#0088bb", "#00ccff"],
    )


def _text_panel(fig: Any, subtitle: str) -> None:
    """Draw the family right-hand text panel onto ``fig``."""
    ax = fig.add_axes([0.62, 0.0, 0.38, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(
        0.08,
        0.84,
        "SCPN",
        color="white",
        fontsize=36,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.745,
        "MIF LINER",
        color="white",
        fontsize=28,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.695,
        "CORE",
        color="white",
        fontsize=28,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.635,
        subtitle,
        color=CYAN,
        fontsize=11,
        fontfamily="monospace",
        alpha=0.85,
    )
    ax.plot([0.08, 0.85], [0.595, 0.595], color=STEEL, lw=0.8, alpha=0.5)
    y = 0.535
    for label, value in TITLE_METRICS:
        ax.text(
            0.08,
            y,
            f"▸ {label}",
            color="#6688aa",
            fontsize=9,
            fontfamily="monospace",
            alpha=0.9,
        )
        ax.text(
            0.10,
            y - 0.030,
            value,
            color="#99bbdd",
            fontsize=8,
            fontfamily="monospace",
            alpha=0.7,
        )
        y -= 0.072
    ax.text(
        0.08,
        0.06,
        "© 1996–2026 Miroslav Šotek",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.6,
    )
    ax.text(
        0.08,
        0.03,
        "anulum.li | AGPL-3.0",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.5,
    )


def _art_axes(fig: Any) -> Any:
    """Return the borderless left-hand art axes of ``fig``."""
    ax = fig.add_axes([0.0, 0.0, 0.68, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    return ax


def _save(fig: Any, plt: Any, name: str) -> None:
    """Save ``fig`` to ``name`` inside the assets directory and close it."""
    target = OUT_DIR / name
    fig.savefig(target, dpi=DPI, facecolor=BG, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    print(f"generated {target}")


def _core_glow(
    ax: Any,
    centre_x: float,
    centre_z: float,
    core_radius: float,
    halo_radius: float,
) -> None:
    """Draw the glowing magnetised target."""
    grid_x = np.linspace(centre_x - halo_radius, centre_x + halo_radius, 150)
    grid_z = np.linspace(centre_z - halo_radius, centre_z + halo_radius, 150)
    mesh_x, mesh_z = np.meshgrid(grid_x, grid_z)
    rho = np.sqrt((mesh_x - centre_x) ** 2 + (mesh_z - centre_z) ** 2) / core_radius
    ax.contourf(
        mesh_x,
        mesh_z,
        np.exp(-rho * 1.8),
        levels=28,
        cmap=_glow_cmap(),
        alpha=0.92,
    )


def _liner_ring(
    ax: Any,
    centre_x: float,
    centre_z: float,
    inner: float,
    thickness: float,
    segments: int | None = None,
) -> None:
    """Draw a material liner annulus, optionally segmented."""
    theta = np.linspace(0.0, 2.0 * np.pi, 300)
    for radius in (inner, inner + thickness):
        ax.plot(
            centre_x + radius * np.cos(theta),
            centre_z + radius * np.sin(theta),
            color=STEEL,
            lw=2.4,
            alpha=0.95,
        )
    if segments:
        for index in range(segments):
            angle = 2.0 * np.pi * index / segments
            ax.plot(
                [
                    centre_x + inner * np.cos(angle),
                    centre_x + (inner + thickness) * np.cos(angle),
                ],
                [
                    centre_z + inner * np.sin(angle),
                    centre_z + (inner + thickness) * np.sin(angle),
                ],
                color=STEEL,
                lw=1.45,
                alpha=0.76,
            )


def generate_liner_closing() -> None:
    """Generate ``repo_header.png``: the liner closing on the target."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(-2.9, 2.9)
    ax.set_ylim(-1.45, 1.45)
    ax.set_aspect("equal")

    theta = np.linspace(0.0, 2.0 * np.pi, 300)

    _core_glow(ax, 0.0, 0.0, 0.34, 1.0)
    ax.plot(
        0.32 * np.cos(theta),
        0.32 * np.sin(theta),
        color=CYAN,
        lw=1.7,
        alpha=0.95,
    )
    for radius, count in ((0.0, 1), (0.17, 6)):
        for index in range(count):
            angle = 2.0 * np.pi * index / max(count, 1)
            ax.plot(
                radius * np.cos(angle),
                radius * np.sin(angle),
                "o",
                color=MAGENTA,
                ms=4,
                alpha=0.9,
            )
    ax.text(
        0.0,
        -0.56,
        "premagnetised target",
        color=MAGENTA,
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )

    _liner_ring(ax, 0.0, 0.0, 0.86, 0.20, segments=24)
    ax.text(
        1.28,
        0.86,
        "material liner",
        color="#8899aa",
        fontsize=8.5,
        fontfamily="monospace",
        alpha=0.9,
    )

    for index in range(16):
        angle = 2.0 * np.pi * index / 16
        outer = (0.80 * np.cos(angle), 0.80 * np.sin(angle))
        inner = (0.60 * np.cos(angle), 0.60 * np.sin(angle))
        ax.annotate(
            "",
            xy=inner,
            xytext=outer,
            arrowprops={"arrowstyle": "->", "color": PROBE, "lw": 1.2, "alpha": 0.85},
        )
    ax.text(
        -2.62,
        1.24,
        "slow branch · of order 10² m/s",
        color=PROBE,
        fontsize=8.5,
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        -2.62,
        0.98,
        "milliseconds, not nanoseconds",
        color="#667799",
        fontsize=7.5,
        fontfamily="monospace",
        alpha=0.9,
    )

    ax.text(
        0.0,
        -1.32,
        "matter compresses the magnetised plasma · LA-7686-MS (1979)",
        color="#445566",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "Matter As The Compressor")
    _save(fig, plt, "repo_header.png")


def generate_velocity_branches() -> None:
    """Generate ``repo_header_velocity_branches.png``: the two branches."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    ax.plot([1.0, 9.2], [4.6, 4.6], color=STEEL, lw=1.6, alpha=0.85)
    decades = [(1, "10¹"), (2, "10²"), (3, "10³"), (4, "10⁴"), (5, "10⁵")]
    for decade, label in decades:
        tick_x = 1.0 + 8.0 * (decade - 1) / 4.0
        ax.plot([tick_x, tick_x], [4.42, 4.78], color=STEEL, lw=1.1, alpha=0.8)
        ax.text(
            tick_x,
            4.05,
            label,
            color="#8899bb",
            fontsize=9,
            fontfamily="monospace",
            ha="center",
        )
    ax.text(
        5.0,
        3.55,
        "implosion velocity  [m/s]",
        color="#8899bb",
        fontsize=9,
        fontfamily="monospace",
        ha="center",
    )

    slow_low = 1.0 + 8.0 * (1.6 - 1) / 4.0
    slow_high = 1.0 + 8.0 * (2.6 - 1) / 4.0
    slow_mid = (slow_low + slow_high) / 2
    ax.fill_between([slow_low, slow_high], 4.95, 6.25, color=GREEN, alpha=0.10)
    ax.text(
        slow_mid,
        6.6,
        "slow material-liner branch",
        color=GREEN,
        fontsize=9,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )
    ax.text(
        slow_mid,
        6.25,
        "of order 10² m/s at NRL",
        color="#99bbdd",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )
    ax.text(
        slow_mid,
        5.55,
        "this repository",
        color=GREEN,
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )

    fast_low = 1.0 + 8.0 * (3.0 - 1) / 4.0
    fast_high = 1.0 + 8.0 * (4.0 - 1) / 4.0
    fast_mid = (fast_low + fast_high) / 2 + 0.35
    ax.fill_between([fast_low, fast_high], 4.95, 6.25, color=RED, alpha=0.08)
    ax.text(
        fast_mid,
        6.6,
        "fast metal-shell branch",
        color=RED,
        fontsize=9,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )
    ax.text(
        fast_mid,
        6.25,
        "10³ – 10⁴ m/s",
        color="#99bbdd",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )
    ax.text(
        fast_mid,
        5.55,
        "outside this class · FLAGGED",
        color=RED,
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )

    bound_x = 1.0 + 8.0 * (3.0 - 1) / 4.0
    ax.plot(
        [bound_x, bound_x],
        [2.6, 7.9],
        color=MAGENTA,
        lw=1.6,
        alpha=0.9,
        ls=(0, (5, 3)),
    )
    ax.text(
        bound_x,
        8.2,
        "declared advisory bound · 1 km/s",
        color=MAGENTA,
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )

    ax.text(
        5.0,
        1.5,
        "the branch attribution follows the cited assessment, not convenience",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
    )
    ax.text(
        5.0,
        1.12,
        "Moses, Krakowski & Miller, LA-7686-MS (1979), Introduction",
        color="#445566",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "Two Branches, One Honest Bound")
    _save(fig, plt, "repo_header_velocity_branches.png")


def generate_liner_classes() -> None:
    """Generate ``repo_header_liner_classes.png``: the two classes."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(-3.2, 3.2)
    theta = np.linspace(0.0, 2.0 * np.pi, 300)

    centre = 2.6
    _core_glow(ax, centre, 0.15, 0.24, 0.7)
    ax.plot(
        centre + 0.22 * np.cos(theta),
        0.15 + 0.22 * np.sin(theta),
        color=CYAN,
        lw=1.5,
        alpha=0.95,
    )
    ax.plot(centre, 0.15, "o", color=MAGENTA, ms=4, alpha=0.9)
    _liner_ring(ax, centre, 0.15, 0.78, 0.22, segments=20)
    for index in range(12):
        angle = 2.0 * np.pi * index / 12
        ax.annotate(
            "",
            xy=(centre + 0.58 * np.cos(angle), 0.15 + 0.58 * np.sin(angle)),
            xytext=(centre + 0.72 * np.cos(angle), 0.15 + 0.72 * np.sin(angle)),
            arrowprops={"arrowstyle": "->", "color": PROBE, "lw": 1.1, "alpha": 0.8},
        )
    ax.text(
        centre,
        2.05,
        "mechanical shell",
        color="#99bbdd",
        fontsize=9,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )
    ax.text(
        centre,
        -2.15,
        "solid liner, segmented drive",
        color="#445566",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
    )

    centre = 7.4
    _core_glow(ax, centre, 0.15, 0.24, 0.7)
    ax.plot(
        centre + 0.22 * np.cos(theta),
        0.15 + 0.22 * np.sin(theta),
        color=CYAN,
        lw=1.5,
        alpha=0.95,
    )
    ax.plot(centre, 0.15, "o", color=MAGENTA, ms=4, alpha=0.9)
    free_surface = 0.74 + 0.035 * np.sin(9 * theta)
    ax.plot(
        centre + free_surface * np.cos(theta),
        0.15 + free_surface * np.sin(theta),
        color="#7799bb",
        lw=1.6,
        alpha=0.9,
    )
    ax.plot(
        centre + 1.02 * np.cos(theta),
        0.15 + 1.02 * np.sin(theta),
        color=STEEL,
        lw=2.4,
        alpha=0.95,
    )
    for index in range(8):
        angle = 2.0 * np.pi * index / 8
        base_x = centre + 0.88 * np.cos(angle)
        base_y = 0.15 + 0.88 * np.sin(angle)
        delta_x, delta_y = -np.sin(angle) * 0.12, np.cos(angle) * 0.12
        ax.annotate(
            "",
            xy=(base_x + delta_x, base_y + delta_y),
            xytext=(base_x - delta_x, base_y - delta_y),
            arrowprops={
                "arrowstyle": "->",
                "color": "#7799bb",
                "lw": 1.1,
                "alpha": 0.8,
            },
        )
    ax.text(
        centre,
        2.05,
        "liquid liner",
        color="#99bbdd",
        fontsize=9,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )
    ax.text(
        centre,
        -2.15,
        "rotating wall, free inner surface",
        color="#445566",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
    )

    ax.plot([5.0, 5.0], [-1.85, 1.9], color=STEEL, lw=0.8, alpha=0.4)
    ax.text(
        5.0,
        -2.75,
        "both classes carry a premagnetised target · hard invariant",
        color=MAGENTA,
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )
    _text_panel(fig, "Two Liner Classes, One Target Rule")
    _save(fig, plt, "repo_header_liner_classes.png")


if __name__ == "__main__":
    generate_liner_closing()
    generate_velocity_branches()
    generate_liner_classes()
