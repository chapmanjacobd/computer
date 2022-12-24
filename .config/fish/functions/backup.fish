# Defined interactively
function backup --argument source
    set target (string trim --right --chars=/ "$source")
    cp -r --reflink=auto "$source" $target.bak
end
