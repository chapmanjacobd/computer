# Defined interactively
function system.battery.cpu
    sudo ~/.local/bin/ryzenadj --stapm-limit=15000 --fast-limit=15000 --slow-limit=15000
end
