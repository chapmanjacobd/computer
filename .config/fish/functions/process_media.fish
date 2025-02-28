# Defined via `source`
function process_media
    lb shrink -vy (fd -td -d2 processing /mnt/) (fd -td -d1 processing /home/xk/) --move ../processed/ --move-broken ../processed-broken/
end
