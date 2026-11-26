# Defined via `source`
function mam.delete
    lb fs ls --db ~/lb/sites/mam/mam.db $argv -p
    or return
    if confirm
        lb fs ls --db ~/lb/sites/mam/mam.db $argv --soft-delete -pa
    end
end
