# Defined interactively
function cb.append.auto
    set out (mktemp)
    echo $out
    watch.py -- cb $argv >>$out
    cat $out | cb
end
