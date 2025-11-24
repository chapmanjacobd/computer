# Defined interactively
function ps.waiting
    ps -weo pid,stat,wchan:20,args | grep -v ' -             ' | sort -k3
end
