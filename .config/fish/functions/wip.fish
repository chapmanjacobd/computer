# Defined interactively
function wip
    argparse y/yes -- $argv

    if count $argv >/dev/null
        $argv
    end

    if test (git status --porcelain | count) -eq 0
        set _flag_yes true
    end

    git reset
    git add .
    git --no-pager diff HEAD
    git --no-pager diff HEAD | grep TODO
    echo
    git --no-pager diff --stat HEAD
    echo
    git status
    wip_message.py
    if set -q _flag_yes; or gum confirm --default=no
        git commit -m "$(wip_message.py)"
        git pull
        git push
    end
end
