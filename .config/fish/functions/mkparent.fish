# Defined interactively
function mkparent --wraps='mkdir'
    mkdir (path dirname $argv)
end
