# Defined via `source`
function rpm.install --wraps='sudo'
    sudo dnf install --setopt=tsflags=nocrypto $argv
end
