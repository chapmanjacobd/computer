# Defined interactively
function mvlj
    for dfolder in $argv
        mvl ~/.jobs/todo/$dfolder ~/.jobs/done/$dfolder
    end
end
