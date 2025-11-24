# Defined interactively
function ps.blocked
    echo w | sudo tee /proc/sysrq-trigger
    sudo dmesg --human --nopager --decode | match-last-tail 'sysrq: Show Blocked State'
end
