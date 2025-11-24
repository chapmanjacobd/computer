# Defined interactively
function pkill.daemon
    pkill -P (pgrep -f 'systemd --user') $argv
end
