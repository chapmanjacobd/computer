complete -c usb.suspend -f
complete -c usb.suspend -s l -d 'Show the device and USB bus ID only'
complete -c usb.suspend -s v -d 'Verbose output'
complete -c usb.suspend -s h -d 'Show usage'
complete -c usb.suspend -a '(__fish_complete_blockdevice)' -d 'USB device'
