# Defined interactively
function cmdline
    for pid in $argv
        cat /proc/$pid/cmdline | xargs -0 bash -c 'printf "%q " "$0" "$@"'
        echo
    end
end
