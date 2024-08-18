# Defined interactively
function brightness_set
    set min 1
    set max (qdbus local.org_kde_powerdevil /org/kde/Solid/PowerManagement/Actions/BrightnessControl brightnessMax)
    qdbus local.org_kde_powerdevil /org/kde/Solid/PowerManagement/Actions/BrightnessControl setBrightnessSilent (math min $max,(math max $min,$argv))
end
