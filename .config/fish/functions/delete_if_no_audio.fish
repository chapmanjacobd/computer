# Defined via `source`
function delete_if_no_audio --argument f
    if not has_audio "$f"
        echo "$f"
        trash "$f"
    end
end
