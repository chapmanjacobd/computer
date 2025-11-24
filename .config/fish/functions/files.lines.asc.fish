# Defined interactively
function files.lines.asc
    fd -tf . $argv -x cat | string trim | asc
end
