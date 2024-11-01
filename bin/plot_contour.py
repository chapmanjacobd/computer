#!/usr/bin/env python
# Henning Hasemann
# https://leetless.de/posts/terminal-plotting-with-matplotlib-and-kitty/
# plot_contour.py 'sin(x*y) + cos(x) + sin(y)'

import argparse
import subprocess

import numpy as np
from matplotlib import pyplot as plt

plt.style.use("dark_background")


def plot(f, *, xmin=-5, xmax=5, ymin=-5, ymax=5, levels, dpi=200):
    dpi = float(dpi)

    fig, ax = plt.subplots(dpi=dpi)

    xs = np.linspace(float(xmin), float(xmax), 1024)
    ys = np.linspace(float(ymin), float(ymax), 1024)
    X, Y = np.meshgrid(xs, ys)

    ns = {**np.__dict__, **dict(x=X, y=Y)}

    zs = eval(f, ns)
    if callable(zs):
        zs = zs(xs, ys)

    if levels is not None:
        if len(levels) <= 2 and isinstance(levels[0], str):
            n = 15
            if len(levels) >= 2:
                n = int(levels[1])

            functions = {
                'linear': [lambda x: x, lambda x: x],
                'square': [np.sqrt, lambda x: x**2],
                'cubic': [lambda x: x ** (1 / 3), lambda x: x**3],
            }

            f_inv, f = functions[levels[0]]

            levels = np.linspace(
                np.sign(zs.min()) * f_inv(np.abs(zs.min())),
                np.sign(zs.max()) * f_inv(np.abs(zs.max())),
                n,
                endpoint=False,
            )
            levels = np.sign(levels) * f(np.abs(levels))

        c = ax.contour(X, Y, zs, levels, cmap='summer')
    else:
        c = ax.contour(X, Y, zs, cmap='summer')
    ax.clabel(c, inline=True, fontsize=10)
    ax.set_box_aspect(1)

    for spine in ax.spines.values():
        spine.set_edgecolor("grey")
        spine.set_linewidth(2)

    ax.set_aspect("equal")
    ax.grid(color="grey", alpha=0.5)

    fig.savefig("/tmp/plot_contour.png", pad_inches=0.1, bbox_inches="tight")

    subprocess.call(["kitty", "+kitten", "icat", "--align", "left", "/tmp/plot_contour.png"])


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('--xlim', default=[-5, 5], nargs=2)
    p.add_argument('--ylim', default=[-5, 5], nargs=2)
    p.add_argument('--levels', nargs='+', default=None)
    p.add_argument('--dpi', default=200)
    p.add_argument('function')
    args = p.parse_args()

    plot(
        args.function,
        xmin=args.xlim[0],
        xmax=args.xlim[1],
        ymin=args.ylim[0],
        ymax=args.ylim[1],
        levels=args.levels,
        dpi=args.dpi,
    )
