function dl-get-sounds --argument folder
    argparse v/verbose -- $argv

    set done_log ~/.jobs/done/$folder

    cd ~/d/$folder/unsorted/
    for url in (combine ~/.jobs/todo/$folder not $done_log | sort --unique --ignore-case --random-sort)
        timeout -k 28m 26m fish -c "ytea "(string escape $url)" $done_log $_flag_verbose"
    end

    combine ~/.jobs/todo/$folder not (cat ~/.jobs/done/* | psub) | sort --unique | sponge ~/.jobs/todo/$folder
end
