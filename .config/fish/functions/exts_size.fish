# Defined interactively
function exts_size
    set db (tempdb)
    lb fsadd --fs $db .
    lb table (sqlite $db "select replace(path, rtrim(path, replace(path, '.', '' ) ), '') ext, count(*), sum(size) size from media group by 1 order by 3" | psub -s .json) -p
end
