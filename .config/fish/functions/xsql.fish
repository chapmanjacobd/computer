# Defined interactively
function xsql
    parallel lb fs {} -pf -s "$argv" ::: ~/disks/x*.db
end
