# Defined in /tmp/fish.2FTqNn/times1nodata0.fish @ line 2
function times1nodata0
    gdal_calc.py -A "$argv" --outfile="$argv" --calc="A*1" --NoDataValue=0 --co="compress=lzw"
end
