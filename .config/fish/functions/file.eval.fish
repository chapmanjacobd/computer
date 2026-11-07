function file.eval
    set -l unit (basename "$argv").service
    if systemctl --user is-active --quiet $unit
        return 0
    end
    systemd-run --user --unit $unit -p RuntimeMaxSec=200h -p MemoryMax=10G -p MemorySwapMax=20G -p RestartSec=15m -p Restart=on-abnormal -p RestartForceExitStatus=0 --same-dir --collect --service-type=exec --quiet -- fish --private "$argv"
end
