# Defined interactively
function tempfile --wraps='mktemp'
    mktemp --suffix .$argv | tee -a /dev/tty
end
