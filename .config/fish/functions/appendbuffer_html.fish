# Defined interactively
function appendbuffer_html
    set out (mktemp)
    echo $out
    while sleep 0.2
        cat $out (cb_htmlfile) | sponge $out
    end
end
