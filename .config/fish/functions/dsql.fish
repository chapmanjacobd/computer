# Defined interactively
function dsql --wraps='parallel'
    parallel lb fs ls --db {} -pf -s "$argv" ::: ~/disks/*.db
end
