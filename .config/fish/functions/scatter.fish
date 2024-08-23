# Defined interactively
function scatter
    for i in (seq 1 10)
        lb mv (df | sort --human-numeric-sort -k4 | grep /mnt/d | awk '{print $6}' | head -1)$argv (df | sort --human-numeric-sort -k4 | grep /mnt/d | awk '{print $6}' | tail -1)$argv -TS 2Gi
    end
end
