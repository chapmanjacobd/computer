# Defined via `source`
function watts
    set PERCENT (apcaccess -pLOADPCT | sed 's/Percent//')
    set UPSMAXWATTS (apcaccess -pNOMPOWER | sed 's/Watts//')

    echo (math "$PERCENT * $UPSMAXWATTS / 100")
end
