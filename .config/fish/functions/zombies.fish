# Defined interactively
function zombies
    ps axo pid=,stat= | awk '$2~/^Z/ { print $1 }'
end
