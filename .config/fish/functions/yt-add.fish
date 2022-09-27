function yt-add
    set folder $argv[1]
    set url $argv[(count $argv)] # last arg
    set ytopts $argv[2..-2]

    set dfolder ~/d/$folder/unsorted/
    set curatifile "/home/xk/mc/""$folder"".txt"

    if test (count $argv) -lt 2
        return 5
    end

    if grep -qix "$url" /home/xk/mc/*
        return 1
    end

    if not test -d $dfolder
        return 2
    end

    echo $url >>$curatifile
    yt-dlp --cookies-from-browser firefox --flat-playlist --print "%(url)s" $ytopts $url | tee -a ~/.jobs/todo/$folder
end
complete -f -k -c yt-add -a "(__fish_complete_directories ~/d/ DFOLDER | sed 's|/home/xk/d/\(.*\)/|\1|' )"
complete -f -k -c yt-add -a "(fd . ~/mc/ -E '*reddit*' -etxt -x cat)"
