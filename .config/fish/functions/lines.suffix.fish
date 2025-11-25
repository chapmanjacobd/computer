# Defined interactively
function lines.suffix --description 'Add suffix to every line (filter)' --argument-names suffix
    if test -z "$suffix"
        echo "Error: suffix argument is required" >&2
        return 1
    end

    python3 -S -c "
import sys

suffix = '$suffix'
for line in sys.stdin:
    line = line.rstrip('\r\n')
    print(f'{line}{suffix}')
"
end
