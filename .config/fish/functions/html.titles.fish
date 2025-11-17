# Defined interactively
function html.titles
    xidel -s - -e '//@title' | unique
end
