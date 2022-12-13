# Defined in /tmp/fish.1r7oen/fish_greeting.fish @ line 2
function fish_greeting
    cat /proc/loadavg | cut -d' ' -f 2
    #set article (/usr/bin/ls -p  ~/placedata-ascii/wikipedia_text/ |grep -v / | shuf -n 1)
    #set_color -o -u
    #echo (string replace '_' ' ' (string replace '.txt' '' (string unescape --style=url $article))) | sed 's/.*/\L&/; s/[a-z]*/\u&/g' | sed -E 's/ (The|A|Of|I[sn]|For)\b/\L&/g'
    #set_color normal
    #head -7 ~/placedata-ascii/wikipedia_text/$article | cowthink -W 78 -f tux
end
