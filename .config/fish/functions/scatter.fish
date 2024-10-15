# Defined interactively
function scatter
    for i in (seq 1 10)
        python -m xklb.lb mv (df | sort --human-numeric-sort -k4 | grep /mnt/d | awk '{print $6}' | head -1)$argv (df | sort --human-numeric-sort -k4 | grep /mnt/d | awk '{print $6}' | tail -n 2 | head -1)$argv -v -l 1
    end
end
