# Defined interactively
function renamed --wraps='git status'
    git status -z $argv \
        | string split0 \
        | while read -l s
        if test (string sub -s 1 -l 1 $s) = R
            string split " -> " (string sub -s 4 $s) | tail -n1
        end
    end
end
