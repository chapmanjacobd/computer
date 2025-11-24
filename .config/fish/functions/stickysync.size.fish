# Defined via `source`
function stickysync.size --argument historyfile from
    set new_files (mktemp)
    combine (ssh backup "cd $from && fd -S+1b --changed-before '24 hours'" | psub) not $historyfile >$new_files

    cat $new_files | ssh backup 'd/_qbittorrent/ && parallel du -b {} 2>/dev/null | cut -d\t -f1 | lines.sum.fish | bytes2human'
end
