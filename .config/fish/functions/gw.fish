# Defined in /home/xk/.config/fish/functions/gw.fish @ line 2
function gw --wraps=gradle
    set -l wt_root "$HOME/.git-worktrees"
    mkdir -p $wt_root

    set -l branch (branchname $argv)
    set -l target_path "$wt_root/$branch"

    git worktree add -b $branch $target_path (git main)

    cd $target_path
end
