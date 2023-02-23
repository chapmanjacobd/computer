# Defined interactively
function wipm
    git add .
    git --no-pager diff HEAD
    git --no-pager diff HEAD | grep TODO
    git diff --stat HEAD
    echo
    git status
    if gum confirm --default=no
        git commit -m "$argv"
        git pull
        git push
    else
        return 1
    end
end
