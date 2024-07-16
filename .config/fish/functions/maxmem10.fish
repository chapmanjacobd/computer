# Defined interactively
function maxmem10
    systemd-run --user -p MemoryMax=10G -p MemorySwapMax=1G --shell -q
end
