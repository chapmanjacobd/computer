#!/bin/bash

# Translate the clipboard with trans and open the result in an editor.
# Output path and languages can be changed below; `trans -T` lists languages.

out="${HOME}/.scripts/translation.txt"
mkdir -p "$(dirname "$out")"

cb -r | trans -no-bidi -show-languages no -show-alternatives no en:ar >"$out"

if command -v kate >/dev/null 2>&1; then
    kate "$out" >/dev/null 2>&1 &
else
    xdg-open "$out" >/dev/null 2>&1 &
fi
