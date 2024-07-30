# Defined interactively
function wipm
    git add .
    rg -i --no-heading todo:
    git --no-pager diff HEAD
    git --no-pager diff HEAD | grep TODO
    git diff --stat HEAD
    echo
    git status
    if gum confirm --default=no
        git utccommit -m "$argv"
        git pull
        git push
    else
        return 1
    end
end
