# Defined interactively
function mvljs --argument s
    for folder in ~/.jobs/todo/*
        set dfolder (basename "$folder")
        mvl -s"$s" ~/.jobs/todo/$dfolder ~/.jobs/done/$dfolder
    end
end
