# Defined interactively
function gitls-commits
    git ls-files --sparse --full-name -z | xargs -0 -I FILE echo "printf '%s\tFILE\n' (git rev-list HEAD --count -- FILE)" | parallel -j40 | sort --general-numeric-sort
end
