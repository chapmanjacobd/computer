# Defined interactively
function trash.check
    for mnt in $argv
        for d in $mnt/.Tras*/*/files/
            NO_COLOR=1 ncdu "$d"
        end
    end
end
