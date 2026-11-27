# Defined interactively
function file.lines.count --wraps='wc'
    wc -l $argv | cut -f1 -d ' '
end
