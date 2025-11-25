# Defined via `source`
function file.handles
    # sudo lsof +c0 (mountpoints) 2>/dev/null | grep -vE '^COMMAND' | lines.coln 1 | asc
    cat /proc/sys/fs/file-nr
    sudo lsfd --summary
end
