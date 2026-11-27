# Defined interactively
function file.prepend --wraps='mv'
    set tmpfile (mktemp --tmpdir=(path dirname "$argv"))

    file.eof.newline.awk | cat - "$argv" >>"$tmpfile"
    mv "$tmpfile" "$argv"
end
