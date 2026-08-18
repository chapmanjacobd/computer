# Defined via `source`
function folders.locate -w plocate
    plocate $argv | folder.exists --all | unique | fzf.multi
end
