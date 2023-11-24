# Defined interactively
function appendbuffer
    set out (mktemp)
    echo $out
    watch.py -- cb $argv >>$out
    cat $out | cb
end
