function unardel
    for f in $argv
        not /usr/bin/unar -q -o (path dirname "$f") -d "$f" &| grep -i password
        and rm "$f"
    end
end
