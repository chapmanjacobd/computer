# Defined interactively
function cb.html.plaintext
    lb extract-text --skip-links --local-file (cb.file.html) | lb cs --groups | jq -r '.[] | .grouped_paths | "\n" + join("\n")'
end
