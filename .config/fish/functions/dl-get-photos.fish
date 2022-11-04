function dl-get-photos --argument folder
    set done_log ~/.jobs/done/$folder

    cd ~/d/$folder/unsorted/
    for url in (combine ~/.jobs/todo/$folder not ~/.jobs/done/$folder | sort --unique --ignore-case --random-sort)
        timeout -k 28m 26m gallery-dl --quiet --download-archive $HOME/.local/share/gallerydl.sqlite3 $url

        if test $status -eq 0 -o $status -eq 4 -o $status -eq 8 -o $status -eq 32
            echo $url >>~/.jobs/done/$folder
        else
            timeout -k 28m 26m fish -c "yte "(string escape $url)" $done_log"
        end
    end

    combine ~/.jobs/todo/$folder not (cat ~/.jobs/done/* | psub) | sort --unique | sponge ~/.jobs/todo/$folder
end
