# Defined interactively
function screen.blank.no
    kwriteconfig5 --file powermanagementprofilesrc --group AC --group DPMSControl --key idleTime 99999
    qdbus org.freedesktop.PowerManagement /org/kde/Solid/PowerManagement reparseConfiguration
end
