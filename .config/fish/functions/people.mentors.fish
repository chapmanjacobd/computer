# Defined interactively
function people.mentors
    set file ~/j/social/people.mentors.md
    echo "$argv" | string split / | string trim | cat - "$file" | sort --unique --ignore-case | sponge "$file"
end
