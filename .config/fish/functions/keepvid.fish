# Defined via `source`
function keepvid
    cp "$argv" ~/d/77_Library/
    set f (basename "$argv")
    ffsmall "$HOME/d/77_Library/$f"
end
