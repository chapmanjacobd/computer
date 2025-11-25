# Defined interactively
function random.float --argument low high
    math (random $low $high) / 1000
end
