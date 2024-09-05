function eval-file
    for j in (cat $argv)
        echo $j
        systemd-run --user -p RuntimeMaxSec=10h -p MemoryMax=10G -p MemorySwapMax=20G --same-dir --wait --collect --service-type=exec -- fish -c "$j"
    end
end
