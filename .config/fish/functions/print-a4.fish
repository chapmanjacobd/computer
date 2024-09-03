# Defined interactively
function print-a4
    convert $argv -gravity center -background white -extent 2480x3508 (path change-extension .a4.pdf "$argv")
end
