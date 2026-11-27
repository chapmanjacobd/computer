# Defined interactively
function sdb --wraps='lb'
    for db in ~/mc/*.db ~/lb/tabs.db ~/lb/dl/*.db
        echo $db
        lb database search $db media $argv
    end
end
