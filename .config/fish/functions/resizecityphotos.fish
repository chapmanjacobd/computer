# Defined in - @ line 2
function resizecityphotos
    cd /home/xk/dataprojects/travelplanner/cityphotos/original/
    mogrify -path /home/xk/dataprojects/travelplanner/cityphotos/web/view/ -strip -interlace Plane -sampling-factor 4:2:0 -quality 85% -colorspace RGB -format jpg -resize "900x270^" -gravity center -crop 900x270+0+0 +repage *.jpg
    mogrify -path /home/xk/dataprojects/travelplanner/cityphotos/web/detail/ -strip -interlace Plane -sampling-factor 4:2:0 -quality 85% -colorspace RGB -format jpg -resize "2048x1080^" -gravity center -crop 2048x1080+0+0 +repage *.jpg
end
