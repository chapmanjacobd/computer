# Defined interactively
function folders.eval
    for folder in (fd -td -d1 -I)
        echo $folder
        $argv $folder
    end
end
