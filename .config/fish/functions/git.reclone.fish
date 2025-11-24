# Defined via `source`
function git.reclone
    set tmp_fifo (mktemp -u)
    mkfifo $tmp_fifo
    git fast-export --signed-tags=strip --all >$tmp_fifo &
    mkcd ../newrepo/
    git fast-import <$tmp_fifo
    rm $tmp_fifo
end
