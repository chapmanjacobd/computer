# Defined interactively
function stderr.test
    echo "this is stdout"
    echo "this is stderr" >&2
end
