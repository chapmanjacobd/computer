# Defined via `source`
function rsync.stdin --wraps='rsync'
    set tempfile (mktemp)
    cat >$tempfile
    rsync -ahz --remove-sent-files $tempfile $argv
    or echo $tempfile
end
