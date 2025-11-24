# Defined interactively
function system.settings.nomachine.colemak.dh
    sudo cp /usr/share/X11/xkb/symbols/us /usr/NX/share/X11/xkb/symbols/us
    setxkbmap -device (xinput list | grep -Eo "Virtual core XTEST keyboard\s*id\=[0-9]{1,2}" | cut -d= -f 2) -model pc105 -layout us -variant colemak_dh
end
