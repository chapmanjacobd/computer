# Defined via `source`
function keepvid
    cp "$argv" ~/d/77_Library/
    set f (basename "$argv[1]")
    ffsmall "$HOME/d/77_Library/$f" $argv[2..-1]
end
