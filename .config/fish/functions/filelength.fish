# Defined interactively
function filelength
    wc -l $argv | cut -f1 -d ' '
end
