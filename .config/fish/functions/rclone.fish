# Defined interactively
function rclone
    command rclone --transfers 10 --multi-thread-streams 4 --progress --metadata --human-readable --fast-list --error-on-no-transfer --checkers 18 $argv
end
