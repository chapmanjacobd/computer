# Defined interactively
function gws --argument-names query
    set -l selection (git worktree list --porcelain | \
                    string match -r "^worktree .*" | \
                    string replace "worktree " "" | \
                    fzf --query "$query" \
                        --select-1 \
                        --exit-0 \
                        --header "Jump to Worktree" \
                        --preview 'set -l dir {}; 
                       git -C $dir branch --show-current | xargs -I % echo "Branch: %";
                       echo "---";
                       git -C $dir status -sb; 
                       echo "---";
                       git -C $dir diff --stat' \
                        --preview-window 'right:60%')

    if test -n "$selection"
        cd "$selection"
    end
end
