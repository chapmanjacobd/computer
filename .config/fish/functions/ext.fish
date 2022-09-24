# Defined interactively
function ext
awk -F'.' '{print $NF}'
end
