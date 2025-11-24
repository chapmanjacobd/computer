# Defined in /home/xk/.config/fish/functions/match-trunc-tail.fish @ line 2
function file.truncate.until --argument file word
    set word (string replace \/ \\\/ -- (string escape --style=regex "$word"))

    set count (grep -c "$word" "$file")
    echo $count

    if test -n "$word" -a $count -eq 1
        sed -n "/$word/",'$p' "$file" | sponge "$file"
    end
end
