# Defined interactively
function dupcode

    sort **py | uniq --count | sort --unique --ignore-case
end
