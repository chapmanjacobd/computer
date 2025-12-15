# Defined interactively
function created --wraps='git status'
    git status -z \
        | string split0 \
        | while read -l s
        if test (string sub -s 1 -l 1 $s) = A
            string sub -s 4 $s
        end
    end
end
