# Defined interactively
function appendbuffer
    set out (mktemp)
    echo $out
    while sleep 0.2
        cat $out (cbfile) | dedupe | sponge $out
    end
    cat $out | cb
end
