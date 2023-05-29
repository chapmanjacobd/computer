# Defined interactively
function maxmem10
    systemd-run --user --scope -p MemoryMax=10G -p MemorySwapMax=10G fish -c "$argv"
end
