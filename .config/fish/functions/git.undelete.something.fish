# Defined interactively
function git.undelete.something
    set -l file (git log --diff-filter=D --summary | grep "delete mode" | awk '{print $4}' | sort -u | fzf --prompt="Select file to restore: ")

    if test -z "$file"
        return 0
    end

    set -l commit (git rev-list -n 1 HEAD -- "$file")
    git checkout $commit~1 -- "$file"
end
