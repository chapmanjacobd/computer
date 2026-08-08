# Defined interactively
function union_all
    ogr2ogr -f FlatGeobuf (path.new $argv) $argv -dialect sqlite -sql "SELECT ST_Union(geometry) AS geometry FROM 'input'"
end
