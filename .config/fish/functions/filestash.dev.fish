# Defined interactively
function filestash.dev
    /home/xk/github/xk/filestash/

    while true
        pkill filestash
        pkill kiwix-serve
        go build -o dist/filestash cmd/main.go
        b ./dist/filestash
        inotifywait -e modify,create,delete,moved_to,moved_from -r server/ public/
    end

    pkill filestash
    pkill kiwix-serve
end
