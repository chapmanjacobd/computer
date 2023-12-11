# Defined via `source`
function dupreplace --argument duplicate original
    rm "$duplicate"

    for n in (seq 1 10)
        set src (echo "$original" | sed "s|/mnt/d/|/mnt/d$n/|")
        if test -e $src
            set dest (echo "$duplicate" | sed "s|/mnt/d/|/mnt/d$n/|")
            command mkdir -p (path dirname "$dest")
            cp --reflink=always $src "$dest"
        end
    end
end
