function unardel.nodir
    for f in $argv
        not /usr/bin/unar -q -o (path dirname "$f") -D "$f" &| tee /dev/tty | grep -i password
        and rm "$f"
    end
end
