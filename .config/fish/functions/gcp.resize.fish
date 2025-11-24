# Defined interactively
function gcp.resize
    gcloud compute disks resize --size 2500 --zone us-west1-b --quiet $argv
    echo growpart /dev/sda 1
    echo sudo resize2fs /dev/sda1
    echo df -h
end
