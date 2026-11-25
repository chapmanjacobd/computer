# Defined interactively
function git.conflicts.keep.local
    git reset && git ls-files -z --deleted | xargs -0 git checkout --
end
