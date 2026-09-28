# Defined interactively
function lt.search --argument target timer search
    lt -db ~/lb/fs/audio.db -T $timer -ct "$target" -s "$search"
end
