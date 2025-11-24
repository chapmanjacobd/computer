# Defined interactively
function json.to.yaml
    python -c 'import sys, yaml, json; print(yaml.dump(json.loads(sys.stdin.read())))'
end
