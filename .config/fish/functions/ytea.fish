function ytea
    set url $argv[1]
    set video_archive $argv[2]
    set ytopts $argv[3..-1]

    yta --quiet --no-playlist $ytopts "$url" &| tee -a ~/.jobs/ytdlp_errors.txt | read -z ytout

    if test -z "$ytout" -o $pipestatus[1] -eq 0
        # no news is good news
        echo "$url" >>"$video_archive"
    else if echo "$ytout" | grep -qE (ytREs)
        # RE matched
        return
    else if echo "$ytout" | grep -qE (ytUREs)
        # URE matched
        echo "$url" >>"$video_archive"
    else
        echo "$url"
        echo "$ytout"
        echo wtf is this ???
    end

end
