# Defined via `source`
function media.process
    printf 'lb shrink -vy %s --move ../processed/ --move-broken ../processed-broken/ --delete-unplayable\n' (fd -td --exact-depth=2 . /mnt/ | grep -Ev '/lost\+found/|/processed/|/processing-incomplete/|/processed-broken/|/downloading/|/seeding/|/mnt/quest/|/mnt/scratch/') (fd -HI -td -d1 processing /home/xk/) | grep -v /mnt/d/ | sort -uR | head -n (threads.max 2) | tmux.waitgroup
end
