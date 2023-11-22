# Defined via `source`
function filehandles
    sudo lsof +c0 (mountpoints) | coln 1 | asc
end
