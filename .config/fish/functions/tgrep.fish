# Defined interactively
function tgrep
    strace -p (pgrep -fn $argv)
end
