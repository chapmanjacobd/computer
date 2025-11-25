# Defined interactively
function lines.prefix --description 'Add prefix to every line (filter)' --argument-names prefix
    if test -z "$prefix"
        echo "Error: prefix argument is required" >&2
        return 1
    end

    python3 -S -c "
import sys

prefix = '$prefix'
for line in sys.stdin:
    print(f'{prefix}{line}', end='')
"
end
