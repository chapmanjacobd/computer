function json.compact --wraps='jq'
    jq -c . <$argv | sponge $argv
end
