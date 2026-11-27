# Tests for path.validate. Run with: fishtape ~/.config/fish/tests/path.validate.fish

@test "accepts a simple filename" (path.validate foo.txt; echo $status) = 0
@test "accepts spaces inside a filename" (path.validate 'foo bar.txt'; echo $status) = 0
@test "accepts a single character" (path.validate a; echo $status) = 0
@test "accepts a dotfile" (path.validate .hidden; echo $status) = 0
@test "accepts a filename at the 255 character limit" (path.validate (string repeat -n 255 a); echo $status) = 0

@test "rejects an empty filename" (path.validate ''; echo $status) = 1
@test "rejects a leading space" (path.validate ' foo'; echo $status) = 1
@test "rejects a trailing space" (path.validate 'foo '; echo $status) = 1
@test "rejects a slash" (path.validate foo/bar; echo $status) = 1
@test "rejects a colon" (path.validate foo:bar; echo $status) = 1
@test "rejects a filename over 255 characters" (path.validate (string repeat -n 256 a); echo $status) = 1
