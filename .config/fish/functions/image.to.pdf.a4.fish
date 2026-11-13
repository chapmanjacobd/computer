# Defined interactively
function image.to.pdf.a4
    convert $argv -gravity center -background white -extent 2480x3508 (path.withsuffix .a4 -e pdf "$argv[1]")
end
