# Defined via `source`
function chars.ext
    awk -F'.' '{print $NF}' $argv
end
