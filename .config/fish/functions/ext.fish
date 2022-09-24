# Defined via `source`
function ext
    awk -F'.' '{print $NF}' $argv
end
