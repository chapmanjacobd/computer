#!/bin/sh
# xcalib applies per-channel gamma ramps through X11. KWin does not expose a
# Wayland equivalent, so the colour themes remain an X11-only tool.

if [ "${XDG_SESSION_TYPE:-}" = wayland ] || [ -n "${WAYLAND_DISPLAY:-}" ]; then
    echo "xcaliber: RGB gamma themes require X11; use xcalib.dim/xcalib.reset or KDE Night Color on Wayland" >&2
    exit 1
fi

dir=$(cd -- "$(dirname -- "$0")" && pwd)
exec "$dir/xcaliber.x11" "$@"
