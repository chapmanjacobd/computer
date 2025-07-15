# Defined interactively
function folders
    for folder in (fd -td -d1 -I)
        echo $folder
        $argv $folder
    end
end
