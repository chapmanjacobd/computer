function unar
    for f in $argv
        /usr/bin/unar -q "$f"
        and trash "$f"
    end
end
