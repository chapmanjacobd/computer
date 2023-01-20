function logNice
    log -o short-monotonic | tr - ' ' | sed 1d | cut -d' ' -f7- | awk 'BEGIN{RS="\n";ORS="\n\n"}1' | string trim | sed s/entries//g
end
