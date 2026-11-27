# Defined via `source`
function union_all --wraps='ogr2ogr'
    ogr2ogr -f FlatGeobuf (path.new "$argv".fgb) "$argv" -dialect sqlite -sql "SELECT ST_Union(geometry) AS geometry FROM '$(layername "$argv")'"
end
