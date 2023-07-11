# Defined interactively
function headtee --argument file
    set temp (mktemp)
    tee $temp
    cat $temp $file | sponge $file
end
