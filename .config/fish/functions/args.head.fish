# Defined interactively
function args.head
    argparse n/lines= -- $argv
    if set -q _flag_lines
        set n $_flag_lines
    else
        set n 1
    end

    echo (print $argv | head -n$n)
end
