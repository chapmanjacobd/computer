# Defined interactively
function run.noswap
    systemd-run --user --scope -p MemorySwapMax=0M $argv
end
