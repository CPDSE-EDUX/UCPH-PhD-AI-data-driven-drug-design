#!/usr/bin/env python3
"""Render the selectivity calculator's three equations to SVG.

The arithmetic never changes, so the equations ship as images rather than as
markup the browser has to typeset. Glyphs are emitted as paths, so no font has
to be present, and the drawing is near-black on transparency; the app inverts
it for dark mode.

    .venv/bin/python for_instructors/day02/build_equations.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "path"      # No font dependency in the output.
matplotlib.rcParams["mathtext.fontset"] = "dejavusans"
from matplotlib.figure import Figure

OUT = Path(__file__).resolve().parents[2] / "day02" / "apps" / "selectivity"
INK = "#1d1d1f"

EQUATIONS = {
    "eq-delta": r"$\Delta\mathrm{Score} \; = \; \mathrm{score}(\mathrm{2B}) \; - \; \mathrm{score}(\mathrm{2A})$",
    "eq-ki": r"$K_i \; = \; \exp\!\left(\dfrac{\mathrm{score}}{RT}\right)$",
    "eq-fold": r"$\mathrm{fold} \; = \; \dfrac{K_i(\mathrm{2B})}{K_i(\mathrm{2A})} \; = \; \exp\!\left(\dfrac{\Delta\mathrm{Score}}{RT}\right)$",
}


def render(name, formula):
    figure = Figure(figsize=(6, 1.2))
    figure.patch.set_alpha(0)
    text = figure.text(0.01, 0.5, formula, fontsize=19, color=INK,
                       ha="left", va="center")
    target = OUT / f"{name}.svg"
    figure.savefig(target, format="svg", transparent=True,
                   bbox_inches="tight", pad_inches=0.06)

    # The glyphs stay near-black on transparency; referenced through <img> they
    # cannot inherit a CSS colour, so the app inverts the whole image for dark mode.
    svg = target.read_text(encoding="utf-8")
    svg = svg.replace("<!-- Created with matplotlib (https://matplotlib.org/) -->\n", "")
    target.write_text(svg, encoding="utf-8")
    return target, len(svg)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, formula in EQUATIONS.items():
        path, size = render(name, formula)
        print(f"Wrote {path.name} ({size:,} bytes)")
