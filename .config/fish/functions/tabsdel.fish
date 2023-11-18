# Defined interactively
function tabsdel
    lb tabs ~/lb/tabs.db $argv -p
    if confirm
        lb tabs ~/lb/tabs.db $argv --delete
    end
end
