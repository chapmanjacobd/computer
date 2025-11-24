# Defined interactively
function prompt.minimal --description 'A minimal prompt'
    set -g fish_autosuggestion_enabled 0
    fish_config theme choose None

    function fish_prompt
        set last_status $status
        printf '$ '
    end
end
