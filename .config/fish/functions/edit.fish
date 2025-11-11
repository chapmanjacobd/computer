# Defined via `source`
function edit
    set sp ~/.github(path resolve "$argv")

    sudoedit "$argv"

    mkdir (path dirname "$sp")
    sudo rsync --chown=(stat -c '%U:%G' (path dirname "$sp")) "$argv" "$sp"
end
