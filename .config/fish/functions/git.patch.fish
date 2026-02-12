# Defined interactively
function git.patch
    curl -L $argv.patch | git am
end
