# Defined interactively
function filehandles
    sudo lsof / | coln 1 | asc
end
