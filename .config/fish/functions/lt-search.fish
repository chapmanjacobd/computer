# Defined interactively
function lt-search --argument target timer search
    catt -d "$target" set_default
    b lt -ct "$target" -s "$search"
    sleep (math "60*$timer")
    lt-stop
    catt -d "Xylo and Orchestra" set_default
end
