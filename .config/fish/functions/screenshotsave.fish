# Defined interactively
function screenshotsave
    set target ~/d/90_Now_Viewing/Screenshot_(datestamp)

    set i 0
    while test -e "$target$i.jpg"
        set i (math $i + 1)
    end

    xclip -selection clipboard -t image/jpg -o >"$target$i.jpg"
    echo "$target$i.jpg"
end
