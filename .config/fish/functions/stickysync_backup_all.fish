# Defined via `source`
function stickysync_backup_all --argument historyfile from to
    set new_files (mktemp)
    combine (ssh backup "cd $from && fd -S+1b" | psub) not $historyfile >$new_files
    cat $new_files | while read line
        rsync -r --files-from=(echo $line | psub) backup:$from $to
        or echo failed $line
    end
end
