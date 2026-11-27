# Defined interactively
function wt.sync --wraps='lb'
    lb relmv (wtd $argv -pf) ~/sync/video/ -v
end
