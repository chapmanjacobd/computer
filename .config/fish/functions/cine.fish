# Defined interactively
function cine
    set qty 7
    set file ~/mc/_cine
    fish -c 'wip ~/mc/'
    set tabs (head -n $qty $file)
    for tab in $tabs
        echo $tab
        if test http = (string sub --length 4 "$tab")
            firefox "$tab" >/dev/null &
        else
            firefox -url "https://www.google.com/search?q=$tab" -url "https://1337x.to/search/$tab/1/" >/dev/null &
            sleep 0.5
        end
    end
    wait
    sed -i -e 1,"$qty"d $file

    fish -c 'wip -y ~/mc/'
end
