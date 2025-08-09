# Defined via `source`
function html_wrap_quote
    cb | fold -s | sed 's/^/> /'
end
