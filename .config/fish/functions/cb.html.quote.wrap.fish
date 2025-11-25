# Defined via `source`
function cb.html.quote.wrap
    cb | fold -s | sed 's/^/> /'
end
