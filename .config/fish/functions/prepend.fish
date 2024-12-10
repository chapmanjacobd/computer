# Defined interactively
function prepend
    set tmpfile (mktemp --tmpdir=(path dirname "$argv"))

    ensure_newline.awk | cat - "$argv" >> "$tmpfile"
    mv "$tmpfile" "$argv"
end
