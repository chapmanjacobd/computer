# Defined interactively
function sqlite.utils
    command sqlite-utils $argv | tr -d '\r'
end
