# Defined interactively
function loopdev.detach.delete --argument-names dev_lo
    set -l back_files (losetup "$dev_lo" -O BACK-FILE --noheadings)
    sudo losetup --detach "$dev_lo"
    and rm $back_files
end
