# Defined via `source`
function newpath
    set base_name (path resolve "$argv")

    set counter 1
    while test -e "$base_name$counter"
        set counter (math $counter + 1)
    end

    echo $base_name$counter
end
