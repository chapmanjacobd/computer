# Defined via `source`
function backup
    for source in $argv
        set target (string trim --right --chars=/ "$source")
        set backup_suffix ".bak"
        set backup_number 0

        while test -e "$target$backup_suffix$backup_number"
            set backup_number (math $backup_number + 1)
        end

        set backup_target "$target$backup_suffix$backup_number"

        cp -r --reflink=auto "$source" "$backup_target"
    end
end
