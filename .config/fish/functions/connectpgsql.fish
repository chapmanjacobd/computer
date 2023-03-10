function connectpgsql
    ssh -i /home/xk/.ssh/dev_rsa -L 5432:localhost:5432 dev@unli.xyz
end
