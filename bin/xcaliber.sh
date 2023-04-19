#!/bin/sh

# xcaliber.sh
# Assumes a base white theme, and modifies screen using xcalib to create "themes"
# requires: xcalib and rofi (can be adapted to dmenu/slmenu)

list () {

    echo "clear     : -red 1.0  0 100 -green 1.0  0 100 -blue 1.0  0 100"
    echo "lightgray : -red 1.0  0  80 -green 1.0 10  80 -blue 1.0 10  80"
    echo "dark-gray : -red 1.0 25 100 -green 1.0 25 100 -blue 1.0 25 100 -invert"
    echo "gray/blue : -red 1.0 40 100 -green 1.0 40 100 -blue 1.0 50 100 -invert"
    echo "purple    : -red 1.0 30 100 -green 1.0 22 100 -blue 1.0 40 100 -invert"
    echo "aqua      : -red 1.0 12 100 -green 1.0 29 100 -blue 1.0 30 100 -invert"
    echo "blue      : -red 1.0 25 100 -green 1.0 30 100 -blue 1.0 40 100 -invert"
    echo "brown     : -red 1.0 17 100 -green 1.0  0 100 -blue 0.9  0 100 -invert"
    echo "black     : -red 1.0  0 100 -green 1.0  0 100 -blue 1.0  0 100 -invert"
    echo "retro     : -red 1.0  0   1 -green 1.0  0 100 -blue 1.0  0   1 -invert"
    echo "zenburn   : -red 0.5  0 100 -green 0.5  0 100 -blue 1.0  0   1 -invert"

}

sel=$(list | rofi -dmenu -p theme)
test -n "$sel" || exit 0

xcalib -clear
xcalib -alter $(echo $sel | awk '{$1=$2=""; print}')
