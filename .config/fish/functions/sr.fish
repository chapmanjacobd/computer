# Defined interactively
function sr --argument-names find --argument-names replace
    rg -. --no-heading --no-line-number -j1 "$find"

    if confirm
        fd --type file --exec sd "$find" "$replace"
    end
end
