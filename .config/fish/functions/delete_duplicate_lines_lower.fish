# Defined interactively
function delete_duplicate_lines_lower
    cat "$argv" | sed "s/\w*'//g;s/ \+/\n/g" | awk '{ print tolower($0) }' | uniq | sponge "$argv"
end
