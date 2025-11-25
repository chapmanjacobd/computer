# Defined via `source`
function stickysync.backup --argument historyfile from to
    set new_files (mktemp)
    combine (ssh backup "cd $from && fd -S+1b --changed-before '24 hours'" | psub) not $historyfile >$new_files
    cat $new_files | while read line
        rsync -r --files-from=(echo $line | psub) backup:$from $to
        and echo $line >>$historyfile
        or echo failed $line
    end
end
