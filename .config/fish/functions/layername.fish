# Defined interactively
function layername
    ogrinfo -ro -json "$argv" | python3 -c 'import json, sys; print(json.load(sys.stdin)["layers"][0]["name"])'
end
