# Defined interactively
function psd
    echo w | sudo tee /proc/sysrq-trigger
    dmesg --human --nopager --decode
end
