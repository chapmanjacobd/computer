# Defined interactively
function image.shrink
    mogrify -strip -interlace Plane -sampling-factor 4:2:0 -quality 85% -colorspace RGB -format jpg -resize "2048x1080^" -gravity center -crop 2048x1080+0+0 +repage $argv
end
