# Defined interactively
function trace
    strace -p (pgrep -fn $argv)
end
