# Defined interactively
function keepscreenoff
    kwriteconfig5 --file powermanagementprofilesrc --group AC --group DPMSControl --key idleTime 500
    qdbus org.freedesktop.PowerManagement /org/kde/Solid/PowerManagement reparseConfiguration
end
