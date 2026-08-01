# Defined interactively
function files.locate
    for s in $argv
        fd -tf . "$s"
    end | unique | fzf.multi
end
