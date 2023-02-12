function json-compress
    jq -c . <$argv | sponge $argv
end
