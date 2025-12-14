# Defined interactively
function __fish_history_long_preexec --on-event fish_preexec
    if test (count (string split \n -- $argv)) -ge 10
        set -g __fish_ignore_history 1
    end
end
