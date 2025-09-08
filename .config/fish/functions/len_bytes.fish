# Defined via `source`
function len_bytes
    python -c 'import sys; print(len(sys.stdin.read().encode("utf-8")))'
end
