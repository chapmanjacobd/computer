# Defined interactively
function iiab-start
    quickemu --public-dir none --vm ~/iiab/virtual/debian-13.1.0-lxqt.conf --display spice $argv
end
