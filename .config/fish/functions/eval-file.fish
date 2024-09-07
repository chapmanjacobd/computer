function eval-file
    systemd-run --user --unit (basename "$argv") -p RuntimeMaxSec=10h -p MemoryMax=10G -p MemorySwapMax=20G -p RestartSec=15m -p Restart=on-success --same-dir --collect --service-type=exec --quiet -- fish --private "$argv"
end
