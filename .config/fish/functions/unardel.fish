function unardel
    for f in $argv
        /usr/bin/unar -q -o (path dirname "$f") -d "$f"
        and rm "$f"
    end
end
