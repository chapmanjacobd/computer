function lt --wraps='systemd-inhibit'
    systemd-inhibit /home/xk/.local/bin/lb (lt.args) -r $argv
end
