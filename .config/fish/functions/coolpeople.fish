# Defined interactively
function coolpeople
set file ~/j/public/people.mentors.md
echo "$argv" | cat - "$file" | sort --unique --ignore-case | sponge "$file"
end
