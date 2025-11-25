# Defined via `source`
function cb.html.titles
    cb -t text/html | xidel -s - -e '//@title' | unique
end
