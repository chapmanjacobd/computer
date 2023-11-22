# Defined via `source`
function filehandles
    sudo lsof (mountpoints) | coln 1 | asc
end
