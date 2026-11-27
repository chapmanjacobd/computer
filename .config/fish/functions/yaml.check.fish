# Defined interactively
function yaml.check --wraps='python3'
    python3 -c "import yaml; yaml.safe_load(open('$argv'))"
end
