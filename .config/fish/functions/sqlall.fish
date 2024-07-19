# Defined interactively
function sqlall
    for db in (fd -eDB . -HI)
        echo $db
        sqlite $db $argv
    end
end
