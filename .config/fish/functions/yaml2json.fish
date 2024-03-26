# Defined interactively
function yaml2json
    python -c 'import sys, yaml, json; print(json.dumps(yaml.safe_load(sys.stdin.read())))'
end
