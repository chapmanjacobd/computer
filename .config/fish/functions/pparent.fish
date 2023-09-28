# Defined interactively
function pparent
    ps -o ppid --no-headers $argv | string trim
end
