# Defined via `source`
function stickysync_size --argument historyfile from
    set new_files (mktemp)
    combine (ssh backup "cd $from && fd -S+1b --changed-before '24 hours'" | psub) not $historyfile >$new_files

    cat $new_files | ssh backup 'cd $from && xargs -I {} du {}' | cut -d\t -f1 | sum | bytes2human
end
