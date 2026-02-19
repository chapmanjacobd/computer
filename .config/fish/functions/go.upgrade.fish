# Defined interactively
function go.upgrade --argument-names v
    curl -fsSLO https://go.dev/dl/go$v.linux-amd64.tar.gz && sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go$v.linux-amd64.tar.gz && rm go$v.linux-amd64.tar.gz
end
