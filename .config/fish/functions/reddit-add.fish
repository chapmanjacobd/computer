# Defined interactively
function reddit-add --argument folder subr
    set curatifile "/home/xk/mc/""$folder""-reddit.txt"
    set dfolder ~/d/$folder/unsorted/

    if not test (count $argv) -eq 2
        return 5
    end

    if grep -qix $subr /home/xk/mc/*
        return 1
    end

    if not test -d $dfolder
        return 2
    end

    echo $subr >>$curatifile

    reddit-links "$subr" | grep '^http' >>~/.jobs/todo/$folder
end

complete -f -k -c reddit-links-update -c reddit-add -c dl-get-sounds -c dl-get-videos -c dl-get-photos -a "(__fish_complete_directories ~/d/ DFOLDER | sed 's|/home/xk/d/\(.*\)/|\1|' )"
complete -f -k -c reddit-add -c dl-get-sounds -c dl-get-videos -c dl-get-photos -a "(cat ~/mc/*reddit.txt)"
