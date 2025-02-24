# Defined interactively
function systemd-bg --description 'Send the current command to systemd'
    # aspirational
    set -l cmd (commandline -c)
    set -l unit_name (basename $cmd[1])
    set -l unit_name (string replace -a -r '[^a-zA-Z0-9]' - '' $unit_name)
    set -l unit_name "bg-$unit_name$(datestamp).service"

    echo $unit_name
    systemd-run --user --unit $unit_name -p RuntimeMaxSec=800h -p MemoryMax=12G -p MemorySwapMax=6G --same-dir --collect --service-type=exec --quiet -- reptyr $fish_pid
end
