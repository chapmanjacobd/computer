# Defined interactively
function lt-search --argument target timer search
    catt -d "$target" set_default
    lt -T $timer -ct "$target" -s "$search"
    lt-stop
    catt -d "Xylo and Orchestra" set_default
end
