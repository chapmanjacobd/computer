# Defined interactively
function unmerged --wraps='git status'
    git status -z $argv \
        | string split0 \
        | while read -l s
        switch (string sub -s 1 -l 2 $s)
            case DD AU UD UA DU AA UU
                string sub -s 4 $s
        end
    end
end
