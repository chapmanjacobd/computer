# Defined interactively
function gws
    fd -td -d2 . ~/.git-worktrees \
        | fzf --preview 'git -C {} status -sb' \
        | read -l dir
    and cd $dir
end
