# Defined via `source`
function locate_folders -w plocate
    plocate $argv | folder_exists.py --all | unique | fzf-choose-multi
end
