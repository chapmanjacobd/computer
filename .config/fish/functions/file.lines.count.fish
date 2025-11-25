# Defined interactively
function file.lines.count
    wc -l $argv | cut -f1 -d ' '
end
