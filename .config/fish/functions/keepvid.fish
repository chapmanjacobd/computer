# Defined via `source`
function keepvid
    set f (basename "$argv[1]")
    set filen (string split -r -m1 . "$HOME/d/77_Library/$f")[1]
    if test -e "$filen".small.mkv
        return 1
    end

    cp "$argv[1]" ~/d/77_Library/
    ffsmall "$HOME/d/77_Library/$f" $argv[2..-1]
    and /bin/rm "$argv[1]" "$HOME/d/77_Library/$f"

    ln -s "$HOME/d/77_Library/$f" "$argv[1]"
    or rm "$filen".small.mkv
end
