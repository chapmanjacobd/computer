# Defined interactively
function file.prepend
    set tmpfile (mktemp --tmpdir=(path dirname "$argv"))

    ensure_newline.awk | cat - "$argv" >>"$tmpfile"
    mv "$tmpfile" "$argv"
end
