complete -c sqlite3_analyzer -f
complete -c sqlite3_analyzer -l pageinfo -d 'Show how each page is used'
complete -c sqlite3_analyzer -l stats -d 'Output SQL text with database statistics'
complete -c sqlite3_analyzer -l tclsh -d 'Run the built-in TCL interpreter'
complete -c sqlite3_analyzer -l version -d 'Show the version number'
complete -c sqlite3_analyzer -a '(__fish_complete_suffix .db .sqlite .sqlite3)' -d 'Database file'
