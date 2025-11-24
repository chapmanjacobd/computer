# Defined interactively
function findandreplace.all --argument-names find --argument-names replace
    rg -. --no-heading --no-line-number -j1 "$find"

    if confirm
        fd -HI --type file --exec sd "$find" "$replace"
    end
end
