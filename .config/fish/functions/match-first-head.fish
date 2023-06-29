# Defined interactively
function match-first-head --argument pattern
    sed -n '0,/'$pattern'/{//!p}' $argv[2] 
end
