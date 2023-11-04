# Defined interactively
function pparent -w ps
    ps -o ppid --no-headers $argv | string trim
end
