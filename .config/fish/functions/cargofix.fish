# Defined interactively
function cargofix
    cargo fix --broken-code --allow-dirty && cargo clippy --fix --allow-dirty
end
