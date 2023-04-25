# Defined interactively
function lbformat
    ssort && isort . && black --exclude=__pypackages__ .
end
