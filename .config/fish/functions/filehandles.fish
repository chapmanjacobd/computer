# Defined via `source`
function filehandles
    sudo lsof +c0 (mountpoints) 2>/dev/null | grep -vE '^COMMAND' | coln 1 | asc
    cat /proc/sys/fs/file-nr
end
