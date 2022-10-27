# Defined interactively
function wordfreq
    set -l a
    while read line
        set a $a $line
    end
    echo $a | sort | uniq | tr [:upper:] [:lower:] | tr -d [:punct:] | tr -d '\r' | tr '[:space:]' '[\n*]' | grep -v "^\s*\$" | fgrep -v -w -f /usr/share/groff/current/eign | sort | uniq -c | sort -bn
end
