complete -c cb -f
complete -c cb -s r -l get -d 'Read the clipboard even when stdin is not a terminal'
complete -c cb -s t -l type -r -a 'text/plain text/html image/png image/jpeg image/gif image/svg+xml' -d 'MIME type'
