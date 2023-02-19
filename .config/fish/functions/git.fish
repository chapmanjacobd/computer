# Defined interactively
function git
    if contains checkout $argv
        echo 'Reminder: Use `git switch` or `git restore` instead.' >&2
    end
    command git $argv

end
