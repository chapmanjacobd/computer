function unar
    for f in $argv
        /usr/bin/unar -q -d "$f"
        and trash "$f"
    end
end
