# Defined interactively
function img_radial_gradient
    magick $argv -size %wx%h radial-gradient: -colorspace RGB -compose copyopacity -composite $argv
end
