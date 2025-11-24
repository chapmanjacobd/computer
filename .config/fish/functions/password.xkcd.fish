# Defined interactively
function password.xkcd
    for i in (seq 1 25)
        printf "%s\n" (shuf -n (random 3 5) ~/.local/share/words.txt | tr -d '\n')
    end
end
