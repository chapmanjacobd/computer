# Defined interactively
function printnew
    set prev (mktemp)
    set curr (mktemp)
    while $argv >$curr
        and :
        combine $curr not $prev
        cat $curr >>$prev
        sleep 1
    end
    trash $prev $curr
end
