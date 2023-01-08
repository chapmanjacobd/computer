# Defined interactively
function gitls-commits
    git ls-files --sparse --full-name -z | xargs -0 -I FILE -P 20 echo "printf '%s\tFILE\n' (git rev-list HEAD --count -- FILE)" | parallel | sort --general-numeric-sort
end
