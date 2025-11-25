# Defined interactively
function fzf.mpv
    set -l videos
    while read -l line
        set videos $videos $line
    end

    while test (count $videos) -gt 0
        set selected_url (printf "%s\n" $videos | fzf)

        if test -n "$selected_url"
            mpv $selected_url
        else
            break
        end

        set -l index (contains -i $videos $selected_url)
        if test $index -gt 0
            set -e videos[$index]
        end
    end
end
