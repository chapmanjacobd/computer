# Defined via `source`
function rpm.install
    sudo dnf install --setopt=tsflags=nocrypto $argv
end
