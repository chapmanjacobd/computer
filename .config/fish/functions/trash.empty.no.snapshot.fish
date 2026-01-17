# Defined interactively
function trash.empty.no.snapshot
    optparse $argv

    set args (
	  if test -z "$args"
	    trash-list --trash-dirs
	  else
	    for dir in (trash-list --trash-dirs)
	        for arg in $args
	            if string match -q -r $arg $dir
                    echo $dir
                end
	        end
	    end
	  end
	)

    for mnt in $args
        if test -e $mnt/.snapshots/one
            sudo btrfs subvolume delete --commit-each $mnt/.snapshots/one
        end
    end

    for d in $args
        du -hs $d | grep -v ^0 # trash.size
        trash-list --trash-dir $d >>~/.local/share/trashed.txt
    end | sort --human-numeric-sort

    if contains -- -f $opts; or gum confirm --default=no 'Empty trash?'
        for d in $args
            command trash-empty -f --trash-dir $d
        end
    end
end
