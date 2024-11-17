# Defined via `source`
function edit
    set sp (path normalize ~/.github/"$argv")

    sudoedit "$argv"

    mkdir (path dirname "$sp")
    sudo rsync --chown=(stat -c '%U:%G' (path dirname "$sp")) "$argv" "$sp"
end
