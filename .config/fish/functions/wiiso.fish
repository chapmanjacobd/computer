# Defined interactively
function wiiso
    dolphin-tool convert -i "$argv" -f rvz --block_size=131072 --compression=zstd -l 3 -o (path change-extension rvz "$argv")
end
