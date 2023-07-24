# Defined interactively
function cbird-delete-image-similar
    cbird -p.dht 1 -similar -select-result -sort-rev resolution -chop -nuke
end
