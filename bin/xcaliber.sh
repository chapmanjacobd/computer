#!/bin/sh

# xcaliber.sh
# Assumes a base white theme, and modifies screen using xcalib to create "themes"
# requires: xcalib and fzf

list () {

    echo "clear     : -red 1.0  0 100 -green 1.0  0 100 -blue 1.0  0 100"
    echo "lightgray : -red 1.0  0  90 -green 1.0  5  90 -blue 1.0  5  90"
    echo "dark-gray : -red 1.0 12 100 -green 1.0 12 100 -blue 1.0 12 100"
    echo "gray/blue : -red 1.0 20 100 -green 1.0 20 100 -blue 1.0 25 100"
    echo "purple    : -red 1.0 15 100 -green 1.0 10 100 -blue 1.0 20 100"
    echo "aqua      : -red 1.0  6 100 -green 1.0 15 100 -blue 1.0 16 100"
    echo "blue      : -red 1.0 12 100 -green 1.0 16 100 -blue 1.0 20 100"
    echo "brown     : -red 1.0  9 100 -green 1.0  0 100 -blue 0.95  0 100"
    echo "black     : -red 1.0 10 100 -green 1.0 10 100 -blue 1.0 10 100"
    echo "retro     : -red 1.0  0  50 -green 1.0  0 100 -blue 1.0  0  50"
    echo "zenburn   : -red 0.75  0 100 -green 0.75  0 100 -blue 1.0  0  50"

}

usage () {
    echo "Usage: $0 [theme]"
}

if [ "$#" -gt 1 ]; then
    usage >&2
    exit 2
fi

if [ "$#" -eq 1 ]; then
    theme=$1
else
    theme=$(list | awk '{print $1}' | fzf --prompt='theme: ' --height=10 --border)
    test -n "$theme" || exit 0
fi

setting=$(list | awk -v theme="$theme" '$1 == theme {
    $1 = ""
    $2 = ""
    sub(/^[[:space:]]+/, "")
    print
    found = 1
    exit
}')

if [ -z "$setting" ]; then
    echo "Unknown theme: $theme" >&2
    usage >&2
    exit 1
fi

xcalib -clear
if [ "$theme" = clear ]; then
    exit 0
fi

set -- $setting
xcalib "$@" -alter
