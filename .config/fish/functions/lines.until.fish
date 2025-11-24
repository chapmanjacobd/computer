# Defined interactively
function lines.until --argument pattern
    sed -n '0,/'$pattern'/{//!p}' $argv[2]
end
