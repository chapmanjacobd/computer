# Defined interactively
function fzf.choose
    _fzf_wrapper --preview="echo -- {} | string replace --regex '^.*? │ ' '' | fish_indent --ansi" --preview-window="bottom:3:wrap" $argv
end
