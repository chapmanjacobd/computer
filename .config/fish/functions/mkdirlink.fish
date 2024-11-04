# Defined interactively
function mkdirlink
    mkdir -p (readlink $argv)
end
