# Defined interactively
function iiab.start --wraps='quickemu'
    quickemu --public-dir none --vm ~/iiab/virtual/debian-13.1.0-lxqt.conf --display spice $argv
end
