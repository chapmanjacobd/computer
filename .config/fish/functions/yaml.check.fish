# Defined interactively
function yaml.check
    python3 -c "import yaml; yaml.safe_load(open('$argv'))"
end
