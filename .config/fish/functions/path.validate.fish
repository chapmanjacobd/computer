# Defined interactively
function path.validate --description 'check if a string is a valid filename on Mac, Linux, & Windows'
    set fname "$argv[1]"

    # must have at least one letter/number
    echo "$fname" | command grep -Pq '\w+'; or return 1

    # cannot start or end with a space
    echo "$fname" | command grep -Pq '^ .*$'; and return 1
    echo "$fname" | command grep -Pq '^.* $'; and return 1

    # can only contain [a-Z0-9\-_]
    echo "$fname" | command grep -Pq '^[\w\.-][\w \.-]{0,253}?[\w\.-]?$'; or return 1
end
