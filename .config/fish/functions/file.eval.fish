function file.eval
    systemd-run --user --unit (basename "$argv") -p RuntimeMaxSec=200h -p MemoryMax=10G -p MemorySwapMax=20G -p RestartSec=15m -p Restart=on-abnormal -p RestartForceExitStatus=0 --same-dir --collect --service-type=exec --quiet -- fish --private "$argv"
end
