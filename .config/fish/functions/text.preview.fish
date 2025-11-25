# Defined via `source`
function text.preview
    head -n 1 "$argv"

    if test (wc -l "$argv" | awk '{print $1}') -gt 1
        echo ...
        tail -n 1 "$argv"
    end
end
