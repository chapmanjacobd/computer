# Defined interactively
function lsfd_paths
    fd . /proc -tsymlink | grep /fd/ | xargs readlink | grep ^/
end
