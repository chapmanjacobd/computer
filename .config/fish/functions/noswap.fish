# Defined interactively
function noswap
    systemd-run --user --scope -p MemorySwapMax=0M $argv
end
