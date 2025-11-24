function lines.eval
    while read line
        eval $argv "$line"
    end
end
