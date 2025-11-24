# Defined interactively
function ls.fd
    fd . /proc -tsymlink | grep /fd/ | xargs readlink | grep ^/
end
