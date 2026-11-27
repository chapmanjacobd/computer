complete -c gh.merge.squash.wait -f
complete -c gh.merge.squash.wait -n '__fish_is_nth_token 1' -a '(gh pr list --json number --jq ".[].number" 2>/dev/null)' -d 'Pull request'
