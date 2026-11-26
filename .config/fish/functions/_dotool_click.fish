function _dotool_click --argument-names button
    printf 'click %s\n' (string join ' ' -- $button) | _dotool
end
