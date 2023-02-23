# Defined via `source`
function e
    set sp (path normalize ~/.github/"$argv")

    sudo nano "$argv"

    mkdir -p (path dirname "$sp")
    sudo rsync --chown=(stat -c '%U:%G' (path dirname "$sp")) "$argv" "$sp"
end
