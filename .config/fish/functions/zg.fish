# Defined interactively
function zg --argument branch
    if test "$branch" = -
        git switch -
    else
        git checkout (git branch --list | fzf --query $branch --select-1 --exit-0 | string trim)
    end
end
