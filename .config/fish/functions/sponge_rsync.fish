# Defined interactively
function sponge_rsync
    set tempfile (mktemp)
    cat >$tempfile
    rsync -avz --remove-sent-files $tempfile $argv
    or echo $tempfile
end
