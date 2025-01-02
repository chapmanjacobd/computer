# Server bootc

## Build

    podman -c podman-machine-default-root build -t localhost/bootc .

## Test

    podman-bootc run --filesystem ext4 localhost/bootc

## Export

    sudo podman build -t localhost/bootc .
    sudo podman run --rm -it --privileged --security-opt label=type:unconfined_t \
        --pull=newer \
        -v ./output:/output \
        -v /var/lib/containers/storage:/var/lib/containers/storage \
        quay.io/centos-bootc/bootc-image-builder:latest \
        --type qcow2 \
        --rootfs ext4 \
        --local localhost/bootc
