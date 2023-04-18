# Defined interactively
function abbrdel
    filterfile ~/.config/fish/abbreviations "abbr -a -- $argv[1] "
end
