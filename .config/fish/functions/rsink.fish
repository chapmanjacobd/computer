# Defined via `source`
function rsink
    set tempfile (mktemp)
    cat >$tempfile
    rsync -ahz --remove-sent-files $tempfile $argv
    or echo $tempfile
end
