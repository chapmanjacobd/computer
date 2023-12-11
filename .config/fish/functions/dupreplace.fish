# Defined interactively
function dupreplace --argument duplicate original
    rm "$duplicate"

    for n in (seq 1 10)
        set src (echo "$original" | sed "s|/mnt/d/|/mnt/d$n/|")
        if test -e $src
            cp --reflink=always $src (echo "$duplicate" | sed "s|/mnt/d/|/mnt/d$n/|")
        end
    end
end
