# Defined in - @ line 2
function l --description 'alias l=tree -L 3 --sort=mtime --dirsfirst -f -h --prune --du --noreport -up'
    setterm -linewrap off
    tree -Lh 2 --sort=mtime --dirsfirst -d -h --prune --du -up -C $argv
    setterm -linewrap on
end
