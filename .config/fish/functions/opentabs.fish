function opentabs
    argparse 'p/prefix=+' 'n/qty=' -- $argv
    set -l file $argv[1]

    if set -q _flag_prefix
        set pre $_flag_prefix
    else
        set pre 'https://www.google.com/search?q='
    end

    if set -q _flag_qty
        set qty $_flag_qty
    else
        set qty 7
    end

    fish -c 'wip ~/mc/'

    set tabs (head -n $qty $file)
    for tab in $tabs
        if test http = (string sub --length 4 "$tab")
            firefox "$tab" >/dev/null &
        else
            for p in $pre
                firefox "$p$tab" >/dev/null &
            end
        end
        if test $qty -gt 10
            sleep 1.5
        end
    end
    wait
    sed -i -e 1,"$qty"d $file

    fish -c 'wip -y ~/mc/'
end
