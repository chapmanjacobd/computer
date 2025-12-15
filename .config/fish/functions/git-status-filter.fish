# Defined interactively
function git-status-filter
    # usage: git-status-filter X Y [git-status-args...]
    set X $argv[1]
    set Y $argv[2]
    set -e argv[1..2]

    git status -z $argv \
        | string split0 \
        | while read -l s
        if test (string sub -s 1 -l 1 $s) = "$X" \
                -a (string sub -s 2 -l 1 $s) = "$Y"
            string sub -s 4 $s
        end
    end
end
