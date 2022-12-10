# Defined interactively
function wip
    argparse y/yes -- $argv

    if count $argv >/dev/null
        $argv
    end

    if test (git status --porcelain | count) -eq 0
        set _flag_yes true
    end

    git add .
    git --no-pager diff HEAD
    echo
    git diff --stat HEAD
    echo
    git status
    if set -q _flag_yes; or gum confirm
        gitupdate .
        git pull
        git push
    end
end

