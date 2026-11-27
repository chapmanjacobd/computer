complete -c syncthing.audit.log.viewer -f
complete -c syncthing.audit.log.viewer -l path -x -a '(__fish_complete_directories)' -d 'Folder containing the audit log files'
complete -c syncthing.audit.log.viewer -l from -x -d 'Start date as YYYYMMDD'
complete -c syncthing.audit.log.viewer -l to -x -d 'End date as YYYYMMDD'
complete -c syncthing.audit.log.viewer -l name -x -d 'Regular expression to filter synced file paths'
complete -c syncthing.audit.log.viewer -l action -x -d 'Regular expression to filter actions'
complete -c syncthing.audit.log.viewer -l stats -r -d 'Unused option; takes a value'
