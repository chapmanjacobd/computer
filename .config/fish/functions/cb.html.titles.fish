# Defined via `source`
function cb.html.titles
    cb --type text/html | xidel -s - -e '//@title' | unique
end
