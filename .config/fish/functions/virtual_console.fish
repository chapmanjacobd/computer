# Defined interactively
function virtual_console
    fish_config theme choose nothing
    setfont ter-132n.psf.gz  # /usr/lib/kbd/consolefonts/
    echo -en '\e]P0123456'
end
