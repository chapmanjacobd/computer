function _screen.virtual_mode --argument-names output clock hdisplay hsync_start hsync_end htotal vdisplay vsync_start vsync_end vtotal hsync vsync
    # Re-adding an existing mode is harmless; fail only if it cannot be found.
    kscreenctl $output add-custom-mode $clock $hdisplay $hsync_start $hsync_end $htotal $vdisplay $vsync_start $vsync_end $vtotal $hsync $vsync 2>/dev/null

    set -l id (kscreenctl $output list-modes |
        string match -r '^[0-9]+:'$hdisplay'x'$vdisplay'@' |
        string replace -r ':.*' '' |
        head -n 1)
    if test -z "$id"
        echo "screen: custom mode $hdisplay"x"$vdisplay not found" >&2
        return 1
    end

    kscreenctl $output set-mode $id
end
