# Defined via `source`
function titled
    if isatty stdin
        cat $argv | title_case.py | sponge $argv
    else
        cat - | string trim | title_case.py | strip
    end
end
