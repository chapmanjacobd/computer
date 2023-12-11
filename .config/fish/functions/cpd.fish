# Defined via `source`
function cpd --argument s d
    for n in (seq 1 10)
        set src (path resolve "$s" | sed "s|/mnt/d/|/mnt/d$n/|")
        set dest (path resolve "$d" | sed "s|/mnt/d/|/mnt/d$n/|")

        command mkdir -p "$dest"
        cp -r --reflink=always "$src"/* "$dest"
    end
end
