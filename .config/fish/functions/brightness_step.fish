# Defined interactively
function brightness_step
    if test (hostname) = len
        echo 1
    else
        qdbus org.kde.Solid.PowerManagement /org/kde/Solid/PowerManagement/Actions/BrightnessControl org.kde.Solid.PowerManagement.Actions.BrightnessControl.brightnessSteps
    end
end
