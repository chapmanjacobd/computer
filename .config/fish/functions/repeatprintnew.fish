# Defined interactively
function repeatprintnew
    set prev (mktemp)
    set curr (mktemp)
    while $argv >$curr
        and :
        combine $curr not $prev
        cat $curr >>$prev
        sleep 1
    end
    trash-put $prev $curr
end
