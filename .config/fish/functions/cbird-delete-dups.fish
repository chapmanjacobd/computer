# Defined interactively
function cbird-delete-dups
    cbird -dups -select-result -sort-rev resolution -chop -nuke
end
