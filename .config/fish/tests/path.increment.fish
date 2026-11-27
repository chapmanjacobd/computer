# Tests for path.increment. Run with: fishtape ~/.config/fish/tests/path.increment.fish

@test "increments an existing numeric suffix" (path.increment foo.2.txt) = foo.3.txt
@test "increments a multi-digit suffix" (path.increment foo.9.txt) = foo.10.txt
@test "increments a numeric name without an extension" (path.increment foo.2) = foo.3
@test "inserts a counter before a non-numeric extension" (path.increment archive.tar.gz) = archive.tar.1.gz
@test "appends a counter to a file without an extension" (path.increment foo) = foo.1
@test "appends a counter to a dotfile" (path.increment .hidden) = .hidden.1
@test "keeps the directory" (path.increment /tmp/foo.2.txt) = /tmp/foo.3.txt
