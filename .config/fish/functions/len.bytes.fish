# Defined via `source`
function len.bytes
    python -c 'import sys; print(len(sys.stdin.read().encode("utf-8")))'
end
