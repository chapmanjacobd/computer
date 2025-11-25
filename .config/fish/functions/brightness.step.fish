# Defined interactively
function brightness.step
    if test (hostname) = len; and not set -q WAYLAND_DISPLAY
        echo 1
    else
        qdbus org.kde.Solid.PowerManagement /org/kde/Solid/PowerManagement/Actions/BrightnessControl org.kde.Solid.PowerManagement.Actions.BrightnessControl.brightnessSteps
    end
end
