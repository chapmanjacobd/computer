# Defined via `source`
function mam.delete
    lb fs ~/lb/sites/mam/mam.db $argv -p
    or return
    if confirm
        lb fs ~/lb/sites/mam/mam.db $argv --soft-delete -pa
    end
end
