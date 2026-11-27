# Defined interactively
function trace --wraps='strace'
    strace -p (pgrep -fn $argv)
end
