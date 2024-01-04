# Defined via `source`
function keepvid
    set f (basename "$argv[1]")
    set filen (string split -r -m1 . "$HOME/d/archive/video/other/$f")[1]
    if test -e "$filen".small.mkv
        return 1
    end

    cp "$argv[1]" ~/d/archive/video/other/
    if test (du -b "$argv[1]" | cut -f1) -gt (mbytes 400M)
        ffsmall "$HOME/d/archive/video/other/$f" $argv[2..-1]
        and /bin/rm "$HOME/d/archive/video/other/$f"
    end
    /bin/rm "$argv[1]"
end
