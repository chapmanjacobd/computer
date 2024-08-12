# Defined interactively
function update_unli_cities_visas
    ssh unli.xyz -t sudo su admin -c '"cd /home/production/admin/random-city-video-api/; LC_ALL=en_US.UTF-8 ~/.local/bin/pipenv run python ./update_visa.py"'
    ssh unli.xyz -t sudo su -c '"systemctl restart scarlette"'
end
