# Defined interactively
function xsql
    parallel lb fs {} -pf -s "$argv" ::: ~/disks/*.fs.db
    parallel lb fs {} -pf -s "$argv" ::: ~/disks/*/*.fs.db
end
