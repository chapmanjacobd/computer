# Defined via `source`
function folders.locate -w plocate
    plocate $argv | folder_exists.py --all | unique | fzf.choose-multi
end
