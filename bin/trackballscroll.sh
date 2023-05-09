#!/usr/bin/env bash
xinput --set-prop "Logitech USB Trackball" "libinput Scroll Method Enabled" 0 0 1

#xinput set-prop "Logitech USB Trackball" "libinput Scroll Method Enabled" "0" "0" "1"
xinput set-prop "Logitech USB Trackball" "libinput Drag Lock Buttons" "9"
xinput set-prop "Logitech USB Trackball" "libinput Button Scrolling Button" "8"
#xinput set-prop "Logitech M570" "libinput Button Scrolling Button" "8"
#xinput set-prop "Logitech M570" "libinput Scroll Method Enabled" "0" "0" "1"
xinput set-button-map "Logitech USB Trackball" 1 8 3 4 5 6 7 2 9
#xinput set-button-map "Logitech M570" 1 8 3 4 5 6 7 2 9
