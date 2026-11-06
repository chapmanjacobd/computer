#!/bin/bash

current=$(kreadconfig6 --file kwinrc --group Plugins --key monocle_ultrawideEnabled)

if [ "$current" = "true" ]; then
  kwriteconfig6 --file kwinrc --group Plugins --key monocle_ultrawideEnabled false
elif [ "$current" = "false" ]; then
  kwriteconfig6 --file kwinrc --group Plugins --key monocle_ultrawideEnabled true
fi

qdbus org.kde.KWin /KWin reconfigure
