# Defined interactively
function files.lines.asc --wraps='fd'
    fd -tf . $argv -x cat | string trim | asc
end
