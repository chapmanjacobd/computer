# Defined via `source`
function radd --argument dfolder
    lb-dev redditadd -c $dfolder --subreddits --lookback 900 -v reddit/$dfolder.db (cat ~/mc/$dfolder-reddit.txt)
end
