#!/bin/bash

# https://github.com/psyb0t/utils/blob/master/convert-video-to-transparent-gif.sh

# Check if the required arguments were provided
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <video_filename> <transparent_color> [scale_divisor] [framerate]"
    exit 1
fi

# Extract the filename without the extension
filename=$(basename -- "$1")
filename="${filename%.*}"

# Optional scale_divisor and framerate parameters
scale_divisor=${3:-1} # Default to 1 if not provided
framerate=${4:-10}    # Default to 10 if not provided

# Convert the video to a GIF using FFmpeg
ffmpeg -i "$1" -vf "scale=iw/$scale_divisor:ih/$scale_divisor" -r $framerate "${filename}.gif"

# Make the GIF transparent using ImageMagick and overwrite the original GIF
convert -dispose Previous "${filename}.gif" -transparent "$2" "${filename}.gif"

echo "Done. Updated ${filename}.gif with transparency."
