# Defined interactively
function xsql
    parallel lb fs ls --db {} -pf -s "$argv" ::: ~/disks/*.fs.db
    parallel lb fs ls --db {} -pf -s "$argv" ::: ~/disks/*/*.fs.db
end
