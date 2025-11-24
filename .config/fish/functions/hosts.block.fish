function hosts.block
    echo "0.0.0.0 $argv" | sudo tee -a /etc/hosts
end
