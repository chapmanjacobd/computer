# Defined interactively
function syncweb.release --argument-names newver
    ~/github/xk/syncweb-py

    set oldver (awk -F'"' '/^__version__/{print $2}' syncweb/__main__.py)

    sed -i "s|$oldver|$newver|" syncweb/__main__.py

    pyformat.all

    git add .
    rg -i --no-heading todo:
    git --no-pager diff "v$oldver"
    git --no-pager diff "v$oldver" | grep TODO
    git diff --stat "v$oldver"
    echo
    git status
    if gum confirm --default=no
        pdm lock
        git commit -m "$newver"
        git pull
        git push
        git tag -a "v$newver" && git push --tags
    end
end
