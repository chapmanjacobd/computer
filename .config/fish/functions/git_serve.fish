# Defined interactively
function git_serve
    git daemon --reuseaddr --verbose --base-path=$PWD --export-all --enable=receive-pack -- $PWD/.git
end
