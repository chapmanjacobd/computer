# Defined interactively
function cb.html.plaintext
    lb text extract --filter-links --local-html (cb.file.html) | lb text sort cluster --groups | jq -r '.[] | .grouped_paths | "\n" + join("\n")'
end
