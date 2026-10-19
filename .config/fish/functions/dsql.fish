# Defined interactively
function dsql
    parallel lb fs ls {} -pf -s "$argv" ::: ~/disks/*.db
end
