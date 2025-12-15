# Defined via `source`
function untracked --wraps='git status'
    # git ls-files --other --exclude-standard

    git status -z $argv \
        | string split0 \
        | while read -l s
        if test (string sub -s 1 -l 2 $s) = "??"
            string sub -s 4 $s
        end
    end
end
