# Defined interactively
function fish.functions
    if count $argv >/dev/null
        rg "$argv" ~/.config/fish/functions/
    else
        code ~/.config/fish/
    end
end
