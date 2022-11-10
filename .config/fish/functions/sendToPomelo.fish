# Defined in - @ line 2
function sendToPomelo
    rsync -z -P -e "ssh -F /home/xk/.ssh/config_pomelo" $argv jacobchapman@149.28.210.145:/home/devs/jacobchapman
end
