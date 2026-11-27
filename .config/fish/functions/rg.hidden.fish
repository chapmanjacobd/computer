# Defined interactively
function rg.hidden --wraps='rg'
    rg -uu --hidden $argv | rg '(/\.|^\.)'
end
