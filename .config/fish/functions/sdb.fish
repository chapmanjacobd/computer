# Defined interactively
function sdb
    for db in ~/mc/*.db ~/lb/tabs.db ~/lb/dl/*.db
        echo $db
        lb database search $db media $argv
    end
end
