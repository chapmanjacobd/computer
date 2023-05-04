# Defined interactively
function connectpg
    ssh -N -L 5432:localhost:5432 $argv
end
