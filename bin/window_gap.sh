#!/bin/bash

# Get active window ID
window_id=$(xdotool getactivewindow)

# Get screen resolution (adjust as needed)
screen_width=$(xrandr | grep '*' | awk '{print $1}' | cut -d 'x' -f 1)
screen_height=$(xrandr | grep '*' | awk '{print $1}' | cut -d 'x' -f 2)

# Calculate gap size (adjust as needed)
gap_width=768

# Calculate gapped window position and size
gapped_x=$gap_width
gapped_y=0
gapped_width=$((screen_width - 2 * gap_width))
gapped_height=$screen_height

# Check the current window geometry and toggle the gap.
current_geometry=$(xdotool getwindowgeometry $window_id)
current_x=$(echo "$current_geometry" | grep -o "X: [0-9]*" | cut -d ' ' -f 2)

if [ "$current_x" -eq "$gap_width" ]; then
  # Remove gaps (fullscreen)
  xdotool windowmove $window_id 0 0
  xdotool windowsize $window_id $screen_width $screen_height
else
  # Apply gaps
  xdotool windowmove $window_id $gapped_x $gapped_y
  xdotool windowsize $window_id $gapped_width $gapped_height
fi
