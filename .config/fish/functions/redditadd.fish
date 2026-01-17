# Defined interactively
function redditadd --argument reddit_db
    lb redditadd --subreddits -v $reddit_db $argv[2..-1]
end
