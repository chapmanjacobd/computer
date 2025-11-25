function json.compact
    jq -c . <$argv | sponge $argv
end
