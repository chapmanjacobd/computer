# Defined interactively
function pipe_code
    set temp_file (mktemp)
    cat >$temp_file
    code $temp_file

end
