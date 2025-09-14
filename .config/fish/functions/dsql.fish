# Defined interactively
function dsql
    parallel lb fs {} -pf -s "$argv" ::: ~/disks/*.db
end
