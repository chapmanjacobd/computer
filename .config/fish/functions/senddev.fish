# Defined in - @ line 2
function senddev
    rsync -z -P -e "ssh -F /home/xk/.ssh/config_dev" $argv dev@unli.xyz:/home/dev/
end
