# Defined interactively
function run.mem4G --wraps='systemd-run'
    systemd-run --user -p MemoryMax=4G -p MemorySwapMax=1G --pty --pipe --same-dir --wait --collect --service-type=exec --quiet -- $argv
end
