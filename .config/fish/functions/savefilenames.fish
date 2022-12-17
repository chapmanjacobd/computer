function savefilenames
    setterm -linewrap off
    tree -Lh 2 --sort=mtime --dirsfirst -h --prune --du -up -C $argv
    setterm -linewrap on
end
