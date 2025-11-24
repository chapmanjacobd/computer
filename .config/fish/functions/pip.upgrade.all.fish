# Defined interactively
function pip.upgrade.all
    pip list --outdated --format=json | jq -r .[].name | xargs -n1 pip install --upgrade
end
