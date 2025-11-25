# Defined interactively
function findandreplace -a find -a replace
    set -l files (rg -i -. --files-with-matches --fixed-strings "$find" | tee /dev/tty)

    if confirm
        sd --string-mode "$find" "$replace" $files
    end
end
