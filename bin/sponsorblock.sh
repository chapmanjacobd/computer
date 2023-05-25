#!/bin/bash
csv="$HOME/.local/share/sponsorTimes.csv"
grep "^$1" "$csv" | awk -F',' '{print "{\"category\":\""$11"\",\"segment\":["$2","$3"],\"UUID\":\""$7"\"},"""}' | tr -d '\n' | sed 's/^/[/;s/,$/]/'
