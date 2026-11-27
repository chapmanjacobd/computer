# Defined interactively
function xsql --wraps='parallel'
    parallel lb fs ls --db {} -pf -s "$argv" ::: ~/disks/*.fs.db
    parallel lb fs ls --db {} -pf -s "$argv" ::: ~/disks/*/*.fs.db
end
