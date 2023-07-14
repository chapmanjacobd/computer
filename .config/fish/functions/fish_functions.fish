# Defined interactively
function fish_functions
    if count $argv >/dev/null
        rg "$argv" ~/.config/fish/functions/
    else
        code ~/.config/fish/
    end
end
