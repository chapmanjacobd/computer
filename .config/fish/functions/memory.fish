# Defined via `source`
function memory
    lsmem
    sudo dmidecode -t 17 | grep -iE 'part|speed' | sort | uniq -c
end
