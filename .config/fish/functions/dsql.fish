# Defined interactively
function dsql
    parallel lb fs ls --db {} -pf -s "$argv" ::: ~/disks/*.db
end
