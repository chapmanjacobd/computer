# Tests for path.explode. Run with: fishtape ~/.config/fish/tests/path.explode.fish

function path_test_explode
    path.explode $argv | string join '|'
end

@test "splits an absolute path" (path_test_explode /a/b/c.txt) = 'c|txt|/a/b'
@test "splits a relative path with a directory" (path_test_explode a/b/c.txt) = 'c|txt|a/b'
@test "splits a relative filename" (path_test_explode c.txt) = 'c|txt|.'
@test "splits a path without an extension" (path_test_explode /a/b/c) = 'c||/a/b'
@test "splits a filename without an extension" (path_test_explode c) = 'c||.'
@test "keeps only the final extension" (path_test_explode archive.tar.gz) = 'archive.tar|gz|.'
@test "treats a dotfile as having no extension" (path_test_explode .hidden) = '.hidden||.'
@test "splits an absolute dotfile path" (path_test_explode /a/b/.hidden) = '.hidden||/a/b'
