# Defined interactively
function wip
    argparse y/yes -- $argv

    if count $argv >/dev/null
        string length -q -- $argv; and $argv
    end

    if test (git status --porcelain | count) -eq 0
        set _flag_yes true
    end

    git reset
    git add .

    set -l tree_oid (git write-tree)
    set -l parent_oid (git rev-parse HEAD)
    set -l msg (git.wip.message --staged)

    git --no-pager diff $parent_oid $tree_oid
    git --no-pager diff $parent_oid $tree_oid | grep -i TODO
    echo
    git --no-pager diff --stat $parent_oid $tree_oid
    echo
    git status
    echo $msg

    if set -q _flag_yes; or gum confirm --default=no
        set -l commit_oid (git commit-tree $tree_oid -p $parent_oid -m "$msg")
        git update-ref HEAD $commit_oid $parent_oid
        git pull
        git push
    end
end
