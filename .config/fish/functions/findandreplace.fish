# Defined interactively
function findandreplace -a find -a replace
    if set -q argv[3]
        set -l files $argv[3..-1]
        sd --string-mode "$find" "$replace" $files
    else
        set -l files (rg -i -. --files-with-matches --fixed-strings "$find" | tee /dev/tty)

        if confirm
            sd --string-mode "$find" "$replace" $files
        end
    end
end
