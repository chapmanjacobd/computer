# Defined interactively
function podman.compose.cleanup
    podman compose down
    podman rmi (podman compose images -q)
end
