# Defined interactively
function crontab
    echo "use systemd-run"
    return 1

    nano ~/.jobs/crontab
    command crontab -T ~/.jobs/crontab
    and command crontab ~/.jobs/crontab
end
