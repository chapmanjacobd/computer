# Defined interactively
function keepscreenon
    kwriteconfig5 --file powermanagementprofilesrc --group AC --group DPMSControl --key idleTime 99999
    qdbus-qt5 org.freedesktop.PowerManagement /org/kde/Solid/PowerManagement reparseConfiguration
end
