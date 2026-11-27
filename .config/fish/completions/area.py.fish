complete -c area.py -l us-land-km2 -x -d 'US landmass in km²'
complete -c area.py -l overlaps -d 'Also show naive summed area and overlap area'
complete -c area.py -a '(__fish_complete_suffix .shp .zip .gpkg .geojson .json .kml .gpx)' -d 'Vector layer'
