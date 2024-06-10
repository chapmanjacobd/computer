# Defined interactively
function tempfile
    mktemp --suffix .$argv | tee -a /dev/tty
end
