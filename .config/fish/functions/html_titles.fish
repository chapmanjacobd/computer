# Defined via `source`
function html_titles
    cb -t text/html | xidel -s - -e '//@title' | unique
end
