# Defined interactively
function xsql
    parallel lb fs {} -pf -s "$argv" ::: ~/disks/*/*.db
end
