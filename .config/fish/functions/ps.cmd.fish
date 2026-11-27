# Defined interactively
function ps.cmd --wraps='ps'
    ps -o command= --ppid $argv
end
