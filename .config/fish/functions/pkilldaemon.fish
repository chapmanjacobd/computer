# Defined interactively
function pkilldaemon
    pkill -P (pgrep -f 'systemd --user') $argv
end
