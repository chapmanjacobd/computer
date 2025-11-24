# Defined interactively
function image.gradient.radial
    magick $argv -size %wx%h radial-gradient: -colorspace RGB -compose copyopacity -composite $argv
end
