# Defined interactively
function mkdirlink --wraps='mkdir'
    mkdir -p (readlink $argv)
end
