# Defined via `source`
function image.colors
    for space in sRGB RGB HSV LAB
        set -l temp_file (mktemp)

        magick "$argv" -quantize "$space" +dither -colors 6 "$temp_file.tiff"

        echo "Histogram in $space colorspace:"
        magick "$temp_file.tiff" -format %c histogram:info:- | tee "$temp_file.txt"
        pastel color (sed -nre 's/.*(#[0-9A-F]{6,8}) .*/\1/p' "$temp_file.txt")

        rm "$temp_file.tiff" "$temp_file.txt"
    end
end
