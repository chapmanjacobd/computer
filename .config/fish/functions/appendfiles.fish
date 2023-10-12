# Defined via `source`
function appendfiles
    set temp (mktemp)
    tee $temp >/dev/null

    for file in $argv
        cat $temp $file | sponge $file
    end

end
