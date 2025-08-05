# Defined via `source`
function process_media
    lb shrink -vy (fd -td -d2 processing /mnt/ | grep -v /mnt/d/ | grep -v /mnt/dro/) (fd -HI -td -d1 processing /home/xk/) --move ../processed/ --move-broken ../processed-broken/ --delete-unplayable
end
