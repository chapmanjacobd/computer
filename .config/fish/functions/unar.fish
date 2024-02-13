function unar
    for f in $argv
        /usr/bin/unar -q -o (path dirname "$f") -d "$f"
        and trash "$f"
    end
end
