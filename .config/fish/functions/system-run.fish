# Defined interactively
function system-run
    systemd-run --user -p MemoryMax=4G -p MemorySwapMax=1G --pty --pipe --same-dir --wait --collect --service-type=exec --quiet -- $argv
end
