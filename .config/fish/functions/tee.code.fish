# Defined interactively
function tee.code
    set temp_file (mktemp)
    cat >$temp_file
    code $temp_file

end
