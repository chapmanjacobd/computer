# Defined interactively
function argshead
    argparse n/lines= -- $argv
    if set -q _flag_lines
        set n $_flag_lines
    else
        set n 1
    end

    echo $argv | cut -d' ' -f -$n
end
