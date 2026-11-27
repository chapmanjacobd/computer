complete -c mam.search -l title -d 'Match the title (default)'
complete -c mam.search -l no-title -d "Don't match the title"
complete -c mam.search -l author -d 'Match the author (default)'
complete -c mam.search -l no-author -d "Don't match the author"
complete -c mam.search -l narrator -d 'Match the narrator'
complete -c mam.search -l no-narrator -d "Don't match the narrator"
complete -c mam.search -l series -d 'Match the series'
complete -c mam.search -l no-series -d "Don't match the series"
complete -c mam.search -l description -d 'Match the description'
complete -c mam.search -l no-description -d "Don't match the description"
complete -c mam.search -l tags -d 'Match tags'
complete -c mam.search -l no-tags -d "Don't match tags"
complete -c mam.search -l categories -l category -r -d 'Category IDs'
complete -c mam.search -l art-books -d 'Search art books'
complete -c mam.search -l no-art-books -d "Don't search art books"
complete -c mam.search -l books -d 'Search books'
complete -c mam.search -l no-books -d "Don't search books"
complete -c mam.search -l audiobooks -d 'Search audiobooks'
complete -c mam.search -l no-audiobooks -d "Don't search audiobooks"
complete -c mam.search -l comics -d 'Search comics'
complete -c mam.search -l no-comics -d "Don't search comics"
complete -c mam.search -l cookbooks -d 'Search cookbooks'
complete -c mam.search -l no-cookbooks -d "Don't search cookbooks"
complete -c mam.search -l musicology -d 'Search musicology'
complete -c mam.search -l no-musicology -d "Don't search musicology"
complete -c mam.search -l radio -d 'Search radio'
complete -c mam.search -l no-radio -d "Don't search radio"
complete -c mam.search -l search-in -r -d 'Search in torrents or series (default: torrents)'
complete -c mam.search -l series-id -x -d 'Series ID'
complete -c mam.search -l force -d 'Force the search'
complete -c mam.search -l cookie -r -d 'MAM cookie (required)'
complete -c mam.search -l db -r -d 'Override the SQLite database'
complete -c mam.search -s v -l verbose -d 'Increase logging verbosity'
complete -c mam.search -l simulate -l dry-run -d 'Do not write changes'
complete -c mam.search -s y -l no-confirm -d 'Do not ask for confirmation'
