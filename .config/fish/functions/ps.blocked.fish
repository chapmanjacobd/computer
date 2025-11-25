# Defined interactively
function ps.blocked
    echo w | sudo tee /proc/sysrq-trigger
    sudo dmesg --human --nopager --decode | lines.after.last 'sysrq: Show Blocked State'
end
