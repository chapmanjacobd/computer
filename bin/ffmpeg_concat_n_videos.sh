CLIPS=("example_1.mp4" "example_2.mp4")
DESTINATION="concat_example.mp4"

ffmpeg \
    -hide_banner \
    -loglevel verbose \
    -f concat \
    -safe 0 \
    -auto_convert 0 \
    -err_detect ignore_err \
    -i <(
        while read -r; do
            echo "file '$REPLY'"
        done <<< "${CLIPS[*]}"
    ) \
    -copy_unknown \
    -map_chapters 0 \
    -c copy \
    "$DESTINATION"
