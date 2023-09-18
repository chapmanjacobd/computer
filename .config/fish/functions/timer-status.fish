# Defined interactively
function timer-status
    journalctl --user -xn 999999 -u $argv
end
