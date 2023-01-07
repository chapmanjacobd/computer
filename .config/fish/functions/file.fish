# Defined interactively
function file
if isatty stdin
command file $argv
else
xargs -I FILE file -b FILE
end
end
