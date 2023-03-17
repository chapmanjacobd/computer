# Defined interactively
function duplines
    fd . $argv -x cat | string trim | asc
end
