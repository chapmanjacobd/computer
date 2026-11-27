complete -c screen -f
complete -c screen -n '__fish_is_nth_token 1' -a on -d 'Turn displays on'
complete -c screen -n '__fish_is_nth_token 1' -a off -d 'Turn displays off'
complete -c screen -n '__fish_is_nth_token 1' -a blank -d 'Blank displays after an idle timeout'
complete -c screen -n '__fish_is_nth_token 1' -a virtual -d 'Add a virtual display mode'
complete -c screen -n '__fish_is_nth_token 2; and contains -- blank (commandline -opc)' -a no -d 'Never blank the display'
complete -c screen -n '__fish_is_nth_token 2; and contains -- virtual (commandline -opc)' -a 2880 -d '2880 virtual mode'
complete -c screen -n '__fish_is_nth_token 2; and contains -- virtual (commandline -opc)' -a laptop -d 'Laptop virtual mode'
complete -c screen -n '__fish_is_nth_token 3; and contains -- virtual (commandline -opc)' -a '(kscreenctl list-outputs --names)' -d 'Output'
