# Defined interactively
function tabsdel
    lb tabs ~/lb/tabs.db $argv -p
    or return
    if confirm
        lb tabs ~/lb/tabs.db $argv --soft-delete -p
    end
end
