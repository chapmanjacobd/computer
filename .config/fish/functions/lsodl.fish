# Defined interactively
function lsodl
    repeat eval "lsof /mnt/d/ | grep -v 'r  '| coln 0 | sed 's|.part.*||' " | unique
end
