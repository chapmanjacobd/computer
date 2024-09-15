# Defined interactively
function cargorelease --argument newver
    if test (git diff; git diff --stat | count) -gt 0
        git diff
        git diff --stat
        if gum confirm --default=no
            git add .
        end
    end

    git diff --staged
    git diff --staged --stat
    git status --untracked-files
    if gum confirm --default=no
        set oldver (awk -F'"' '/^version = /{print $2}' Cargo.toml)

        sed -i "s|$oldver|$newver|" Cargo.toml
        git commit -m "$newver"
        git pull
        git push
        cargo fmt
        git add .
        cargo fix --allow-staged --tests
        git add .
        cargo clippy --fix --allow-staged --tests
        git add .
        if gum confirm --default=no
            git amend
        else
            git restore --source=HEAD --staged --worktree -- .
        end
        git tag -a "v$newver" && git push --tags
    end
end
