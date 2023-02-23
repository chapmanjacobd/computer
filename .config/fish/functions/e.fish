# Defined via `source`
function e
    set sp (path normalize ~/.github/"$argv")

    sudo nano "$argv"

    mkdir -p (path dirname "$sp")
    cp "$argv" "$sp"
end
