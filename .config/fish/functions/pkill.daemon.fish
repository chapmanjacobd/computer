# Defined interactively
function pkill.daemon --wraps='pkill'
    pkill -P (pgrep -f 'systemd --user') $argv
end
