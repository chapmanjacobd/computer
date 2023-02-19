#!/bin/sh
echo "($1 * 220.0) / 1" | bc > /sys/class/backlight/amdgpu_bl0/brightness
