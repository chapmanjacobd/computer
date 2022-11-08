function updateMapHistory
    ssh jacobchapman@pomelotravel.com -i ~/.ssh/pomelo-bluehost 'sudo su pomelo -c \'/bin/bash ~/maps/update-map-history.sh\''
end
