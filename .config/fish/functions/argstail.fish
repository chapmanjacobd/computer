# Defined interactively
function argstail
    argparse n/lines= -- $argv
    if set -q _flag_lines
        set n $_flag_lines
    else
        set n 1
    end

    echo $argv | string split ' ' | tail -n $n | string join ' '
end
