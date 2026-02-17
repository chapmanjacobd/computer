# Defined interactively
function sdb
    for db in ~/mc/*.db ~/lb/tabs.db
        echo $db
        lb sdb $db media $argv
    end
end
