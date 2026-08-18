# Defined via `source`
function findandreplace.regex --argument-names find replace
    if set -q argv[3]
        set -l files $argv[3..-1]
        sd "$find" "$replace" $files
    else
        set -l files (rg -i -. --files-with-matches "$find" | tee /dev/tty)

        if test (count $files) -gt 0; and confirm
            sd "$find" "$replace" $files
        end
    end
end
