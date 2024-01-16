# Defined interactively
function reccomendations_html
    lb extract-text --skip-links --local-file (cb_htmlfile) | lb cs --groups | jq -r '.[] | .grouped_paths | "\n" + join("\n")'
end
