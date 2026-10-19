# Defined interactively
function tabsdel
    lb tabs open ~/lb/tabs.db $argv -p
    or return
    if confirm
        lb tabs open ~/lb/tabs.db $argv --soft-delete -p
    end
end
