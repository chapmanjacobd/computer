# Defined interactively
function remove-broken-symlinks
    find $argv -type l ! -readable -print -delete
end
