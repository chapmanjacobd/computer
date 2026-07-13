# Defined interactively
function cbi.file
    set -l file $argv[1]

    if test -n "$WAYLAND_DISPLAY"
        wl-copy <$file
    else
        set -l mime (file --brief --mime-type $file)
        xclip -selection clipboard -t $mime <$file
    end
end
