complete -c killport -f -a '(lsof -nP -iTCP -sTCP:LISTEN -F n 2>/dev/null | string replace -r "^n.*:" "" | string match -r "^\d+\$" | sort -u)' -d 'Listening port'
