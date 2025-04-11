# Defined interactively
function brightness_set
    set min 2
    set max (qdbus org.kde.Solid.PowerManagement /org/kde/Solid/PowerManagement/Actions/BrightnessControl brightnessMax)
    qdbus org.kde.Solid.PowerManagement /org/kde/Solid/PowerManagement/Actions/BrightnessControl setBrightnessSilent (math min $max,(math max $min,$argv))
end
