# Defined via `source`
function findandreplace.regex --argument-names find replace
    set -l files (rg -i -. --files-with-matches "$find" | tee /dev/tty)

    if confirm
        sd "$find" "$replace" $files
    end
end
