# Defined via `source`
function sponge_rsync
    set tempfile (mktemp)
    cat >$tempfile
    rsync -ahz --remove-sent-files $tempfile $argv
    or echo $tempfile
end
