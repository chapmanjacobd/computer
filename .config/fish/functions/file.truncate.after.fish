# Defined in /home/xk/.config/fish/functions/match-trunc-head.fish @ line 2
function file.truncate.after --argument file word
    set word (string replace \/ \\\/ -- (string escape --style=regex "$word"))

    set count (grep -c "$word" "$file")
    echo $count

    if test -n "$word" -a $count -eq 1
        sed -n "1,/$word/p" "$file" | sponge "$file"
    end
end
