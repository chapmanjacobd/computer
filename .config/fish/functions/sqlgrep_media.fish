# Defined interactively
function sqlgrep_media
    for db in $argv[2..-1]
        echo $db
        lb sdb $db media $argv[1]
    end
end
