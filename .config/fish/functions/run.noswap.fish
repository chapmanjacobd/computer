# Defined interactively
function run.noswap --wraps='systemd-run'
    systemd-run --user --scope -p MemorySwapMax=0M $argv
end
