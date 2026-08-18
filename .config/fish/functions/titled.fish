# Defined via `source`
function titled
    if isatty stdin
        cat $argv | text.to.titlecase | sponge $argv
    else
        cat - | string trim | text.to.titlecase | lines.no.empty
    end
end
