# Defined via `source`
function keepvid
    cp "$argv[1]" ~/d/77_Library/
    set f (basename "$argv[1]")
    ffsmall "$HOME/d/77_Library/$f" $argv[2..-1]
    and /bin/rm "$argv[1]" "$HOME/d/77_Library/$f"
end
