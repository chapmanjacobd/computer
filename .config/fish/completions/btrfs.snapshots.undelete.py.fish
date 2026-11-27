complete -c btrfs.snapshots.undelete.py -l snapshot-root -r -f -a '(__fish_complete_directories)' -d 'Snapshot root (default: .snapshots/one/)'
complete -c btrfs.snapshots.undelete.py -n __fish_is_first_arg -F -d 'Diff file'
