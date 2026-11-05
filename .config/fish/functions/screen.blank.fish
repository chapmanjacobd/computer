# Defined interactively
function screen.blank
    kwriteconfig6 --file powermanagementprofilesrc --group AC --group DPMSControl --key idleTime 500
    qdbus org.freedesktop.PowerManagement /org/kde/Solid/PowerManagement reparseConfiguration
end
