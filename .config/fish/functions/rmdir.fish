# Defined via `source`
function rmdir
    for folder in $argv
        command rmdir "$folder" 2>/dev/null

        if test $status -ne 0
            find "$folder" -type d -empty -delete

            if test -d "$folder"
                du -h -d 1 "$folder"
            end
        end
    end
end
