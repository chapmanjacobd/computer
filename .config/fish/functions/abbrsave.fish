# Defined via `source`
function abbrsave
    filterfile ~/.config/fish/abbreviations "abbr -a -U -- $argv[1]"
    echo abbr -a -U -- $argv[1] (string join -- ' ' (string escape -- $argv[2..-1])) >> ~/.config/fish/abbreviations 
end
