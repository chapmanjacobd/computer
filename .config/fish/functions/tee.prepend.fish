# Defined interactively
function tee.prepend --argument file
    set temp (mktemp)
    tee $temp
    cat $temp $file | sponge $file
end
