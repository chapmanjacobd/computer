# Defined interactively
function ps.cmd
    ps -o command= --ppid $argv
end
