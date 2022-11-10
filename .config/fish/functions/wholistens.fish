# Defined interactively
function wholistens --description 'Get open connections on a given port' --argument port
    sudo lsof +c 0 -i :$port
end
