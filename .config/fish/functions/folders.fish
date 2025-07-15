# Defined interactively
function folders
    for folder in (fd -td -d1 -H)
        echo $folder
        $argv $folder
    end
end
