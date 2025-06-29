# Defined interactively
function reset-amdgpu
    echo 1 | sudo tee /sys/class/drm/card1/device/remove
    echo 1 | sudo tee /sys/bus/pci/rescan
end
