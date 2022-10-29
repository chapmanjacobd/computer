# Defined interactively
function wipm
    git add .
    git --no-pager diff HEAD
    git diff --stat HEAD
    echo
    git status
    if gum confirm
        git commit -m "$argv"
        git pull
        git push
    else
        return 1
    end
end
