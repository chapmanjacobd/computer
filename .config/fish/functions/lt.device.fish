# The speaker a machine plays to. Fixed per machine, so it never has to be
# configured: whoever is playing, next/stop/volume land on the right speaker.
# Bedroom on len, Kitchen display on pakon, Bathroom speaker on the phone.
# The whole table is on every machine, so lt.device pakon works from anywhere.
function lt.device --argument host
    set -q host[1]; or set host (hostname)
    switch $host
        case len
            echo Bedroom
        case pakon
            echo Kitchen
        case phone localhost
            echo Bathroom
        case '*'
            echo Bedroom
    end
end
