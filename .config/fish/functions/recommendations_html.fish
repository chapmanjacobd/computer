# Defined interactively
function recommendations_html
    lb extract-text --skip-links --local-file (cb.file.html) | lb cs --groups | jq -r '.[] | .grouped_paths | "\n" + join("\n")'
end
