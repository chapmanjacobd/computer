# Defined interactively
function parallel-stop
    kill -HUP (pgrep -fa parallel | _fzf_wrapper --preview="echo -- {} | string replace --regex '^.*? │ ' '' | fish_indent --ansi" --preview-window="bottom:3:wrap" | cut -d' ' -f1)
end
