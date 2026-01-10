# Defined interactively
function media.process.disk
    printf 'lb shrink -vy %s --move ../processed/ --move-broken ../processed-broken/ --delete-unplayable\n' (fd -td --exact-depth=1 . $argv | grep -Ev '/lost\+found/|/processed/|/processing-incomplete/|/processed-broken/|/downloading/|/seeding/|/mnt/quest/|/mnt/scratch/') | tmux.waitgroup
end
