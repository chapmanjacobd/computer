# Defined via `source`
function dlstatus
    for folder in ~/.jobs/todo/*
        set folder (basename $folder)
        fish -c "combine ~/.jobs/todo/$folder not (cat ~/.jobs/done/* | psub) | sort --unique | sponge ~/.jobs/todo/$folder" &

        printf '%s\t%s\n' (combine ~/.jobs/todo/$folder not ~/.jobs/done/$folder | wc -l) $folder
    end

    wait
end
