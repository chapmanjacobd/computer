# Defined interactively
function duplines
    fd . $argv -x cat | asc
end
