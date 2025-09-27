# Defined interactively
function lt-search --argument target timer search
    # catt -d "$target" set_default
    lt -db ~/lb/fs/audio.db -T $timer -ct "$target" -s "$search"
    # catt -d "Xylo and Orchestra" set_default
end
