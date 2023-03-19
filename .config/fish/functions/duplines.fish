# Defined interactively
function duplines
    fd -tf . $argv -x cat | string trim | asc
end
