# Defined interactively
function system.config.preset
    sudo rm /etc/xdg/plasma-workspace/env/nx-sourceenv.sh

    if not grep (hostnamectl | grep -i "static hostname:" | cut -f2- -d:) /etc/hosts
        echo -e '127.0.0.1\t' $(hostnamectl | grep -i "static hostname:" | cut -f2- -d:) | sudo tee -a /etc/hosts
    end
end
