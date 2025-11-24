# Defined interactively
function git.daemon
    git daemon --reuseaddr --verbose --base-path=$PWD --export-all --enable=receive-pack -- $PWD/.git
end
