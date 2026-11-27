complete -c run.plans -f
complete -c run.plans -l keep-going -d 'Continue after a plan fails'
complete -c run.plans -s h -l help -d 'Show help'
complete -c run.plans -n 'contains -- -- (commandline -opc)' -a '(__fish_complete_command)' -d 'Agent command'
