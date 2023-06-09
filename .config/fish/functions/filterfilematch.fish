# Defined interactively
function filterfilematch --argument file word
    set count (grep -c "$word" "$file")
    echo $count

    if test -n "$word" -a $count -eq 1
        sed -n "1,/$word/p" "$file"
        sed -n "/$word/",'$p' "$file" | sponge "$file"
    end
end
