# Defined interactively
function json2yaml
    python -c 'import sys, yaml, json; print(yaml.dump(json.loads(sys.stdin.read())))'
end
