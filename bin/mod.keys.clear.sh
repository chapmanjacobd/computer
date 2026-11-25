#!/usr/bin/env bash
set -o pipefail

if command -v dotool >/dev/null 2>&1; then
    {
        printf 'keyup leftctrl\n'
        printf 'keyup rightctrl\n'
        printf 'keyup leftshift\n'
        printf 'keyup rightshift\n'
        printf 'keyup leftalt\n'
        printf 'keyup rightalt\n'
        printf 'keyup leftmeta\n'
        printf 'keyup rightmeta\n'
        printf 'keyup capslock\n'
    } | dotool
else
    echo keyup Control_L | xte
    echo keyup Control_R | xte
    echo keyup Shift_L | xte
    echo keyup Shift_R | xte
    echo keyup Meta_L | xte
    echo keyup Meta_R | xte
    echo keyup Alt_L | xte
    echo keyup Alt_R | xte
    echo keyup Super_L | xte
    echo keyup Super_R | xte
fi

if [ "${XDG_SESSION_TYPE:-}" = x11 ]; then
    xset r on
fi
