# Defined interactively
function wip.clean
    git clean -n
    if gum confirm
        git clean -f
    end
    git add .
    git status
    git diff --stat HEAD
    git --no-pager diff HEAD
end
