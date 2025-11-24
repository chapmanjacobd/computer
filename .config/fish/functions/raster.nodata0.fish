# Defined in /tmp/fish.2FTqNn/gdalcalcnodata0.fish @ line 2
function raster.nodata0
    gdal_calc.py -A "$argv" --outfile="$argv" --calc="A*1" --NoDataValue=0 --co="compress=lzw"
end
