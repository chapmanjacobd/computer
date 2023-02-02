# Defined interactively
function volumeup
    if pgrep -f 'catt '
        catt volumeup 2
    else
        vol +2
    end
end
