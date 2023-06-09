# Defined interactively
function filterfilematch --argument file word
    if test -n "$word"; and grep -q "$word" "$file"
        sed -n "1,/$word/p" "$file"
        sed -n "/$word/",'$p' "$file" | sponge "$file"
    end

end
