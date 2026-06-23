# Defined interactively
function git.undelete
    set -l file $argv[1]
    if test -z "$file"
        echo "Usage: git.undelete <file_path>"
        return 1
    end

    set -l commit (git log -n 1 --diff-filter=D --summary | grep "delete mode" | grep "$file" | awk '{print $1}')

    if test -z "$commit"
        # Fallback search if the summary format differs
        set commit (git rev-list -n 1 HEAD -- "$file")
    end

    if test -n "$commit"
        git checkout $commit^ -- "$file"
        echo "Restored $file from commit $commit"
    else
        echo "Error: Could not find deletion history for $file"
        return 1
    end
end
