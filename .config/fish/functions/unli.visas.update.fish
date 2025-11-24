# Defined interactively
function unli.visas.update
    ssh unli.xyz -t 'cd /home/xk/github/cities/; LC_ALL=en_US.UTF-8 ~/.local/bin/pipenv run python ./update_visa.py'
    ssh unli.xyz -t sudo su -c '"systemctl restart city_api.service"'
end
