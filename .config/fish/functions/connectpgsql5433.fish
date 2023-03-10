# Defined in - @ line 2
function connectpgsql5433
    ssh -i /home/xk/.ssh/dev_rsa -L 5433:localhost:5432 dev@unli.xyz
end
