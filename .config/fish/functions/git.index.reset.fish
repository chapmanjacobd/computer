# Defined interactively
function git.index.reset
    trash .git/index
    git reset

    set files
    git status -z \
        | string split0 \
        | while read -l s
        if test (string sub -s 1 -l 2 $s) = " M"
            set -a files (string sub -s 4 $s)
        end
    end

    if test (count $files) -gt 0
        git update-index --skip-worktree -- $files
    end
end
