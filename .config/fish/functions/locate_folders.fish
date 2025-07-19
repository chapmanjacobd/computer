# Defined via `source`
function locate_folders
    plocate $argv | folder_exists.py --all | unique | fzf-choose-multi
end
