# Defined interactively
function inotify.commands
    sudo find /proc -maxdepth 3 -path '/proc/[0-9]*/fd/*' -lname 'anon_inode:inotify' 2>/dev/null | awk -F/ '{print $3}' | sort -u | xargs -I {} ps -p {} -o comm | asc
end
