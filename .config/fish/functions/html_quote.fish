# Defined via `source`
function html_quote
    cb | wrap | sed 's/^/> /'
end
