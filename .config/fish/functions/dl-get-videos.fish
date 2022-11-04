function dl-get-videos
    set folder $argv[1]
    set ytopts (string join -- ' ' (string escape -- $argv[2..-1]))

    set done_log ~/.jobs/done/$folder

    cd ~/d/$folder/unsorted/
    fd --changed-before 3h -epart-Frag100 -epart -eytdl -eunknown_video -x rm
    for url in (combine ~/.jobs/todo/$folder not $done_log | sort --unique --ignore-case --random-sort)
        timeout -k 28m 26m fish -c "yte "(string escape $url)" $done_log $ytopts"
    end
end
