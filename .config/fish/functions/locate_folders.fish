# Defined via `source`
function locate_folders
    plocate $argv | path dirname | unique | folder_exists.py
end
