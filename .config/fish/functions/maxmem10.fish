# Defined interactively
function maxmem10
    systemd-run --user -p MemoryMax=10G -p MemorySwapMax=1G --pty --pipe --same-dir --wait --collect --service-type=exec --quiet $argv
end
