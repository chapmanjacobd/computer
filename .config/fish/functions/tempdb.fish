# Defined interactively
function tempdb
    mktemp --suffix .db | tee /dev/tty
end
