# Defined interactively
function xsql
    parallel lb fs ls {} -pf -s "$argv" ::: ~/disks/*.fs.db
    parallel lb fs ls {} -pf -s "$argv" ::: ~/disks/*/*.fs.db
end
