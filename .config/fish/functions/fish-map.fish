function fish-map
    while read line
        eval $argv "$line"
    end
end
