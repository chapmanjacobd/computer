# Defined interactively
function filterfilematch --argument file word
    if test -n "$word" -a (grep -c "$word" "$file") -eq 1
        sed -n "1,/$word/p" "$file"
        sed -n "/$word/",'$p' "$file" | sponge "$file"
    end

end
