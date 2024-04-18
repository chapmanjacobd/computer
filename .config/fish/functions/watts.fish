# Defined via `source`
function watts
    set PERCENT (apcaccess -pLOADPCT | sed 's/Percent//')
    set UPSMAXWATTS (apcaccess -pNOMPOWER | sed 's/Watts//')
    set watts (math "$PERCENT * $UPSMAXWATTS / 100")
    echo $watts
end
