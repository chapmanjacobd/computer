# Defined via `source`
function rsync.stdin
    set tempfile (mktemp)
    cat >$tempfile
    rsync -ahz --remove-sent-files $tempfile $argv
    or echo $tempfile
end
