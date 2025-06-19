# Defined interactively
function take --description 'Take the first `<n>` lines of stdin (filter)' --argument-names number
    head -$number
end
