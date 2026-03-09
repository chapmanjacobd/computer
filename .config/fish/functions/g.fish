# Defined interactively
function g
    argparse 'p/provider=' 'b/branch=' -- $argv
    set -l args $argv

    set -l wt_root "$HOME/.git-worktrees"
    mkdir -p $wt_root

    if not set -q _flag_branch
        set _flag_branch $args[1]
    end

    set -l target_path "$wt_root/$_flag_branch"

    # 1. Create the worktree
    git worktree add -b $_flag_branch $target_path (git main)

    # 2. Prepare and Edit Prompt Template
    set -l initial_prompt "I am starting work on branch '$_flag_branch'. Provide a technical implementation plan focusing on data architecture and potential edge cases."

    # Use vipe to edit the prompt in $EDITOR
    set -l final_prompt (echo $initial_prompt | vipe)

    switch $_flag_provider
        case qwen
            qwen "$final_prompt" >"$target_path/INIT_PLAN.md"
        case '*'
            gemini prompt "$final_prompt" >"$target_path/INIT_PLAN.md"
    end

    cd $target_path
end
