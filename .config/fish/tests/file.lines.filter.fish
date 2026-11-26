# Tests for file.lines.filter. Run with: fishtape ~/.config/fish/tests/file.lines.filter.fish

set --global file_test_path (mktemp)

function file_test_reset
    printf '%s\n' $argv >$file_test_path
end

function file_test_contents
    string join '|' (cat $file_test_path)
end

file_test_reset alpha BETA gamma

@test "removes matching lines case-insensitively" (file_test_reset alpha BETA gamma; file.lines.filter $file_test_path beta >/dev/null; file_test_contents) = 'alpha|gamma'
@test "keeps the file when the word does not match anything" (file_test_reset alpha; file.lines.filter $file_test_path zeta >/dev/null; file_test_contents) = 'alpha'
@test "ignores an empty word" (file_test_reset alpha; file.lines.filter $file_test_path '' >/dev/null; file_test_contents) = 'alpha'
@test "does not treat a dash-prefixed word as a grep option" (file_test_reset alpha BETA; file.lines.filter $file_test_path -y >/dev/null; file_test_contents) = 'alpha|BETA'
@test "removes every line containing a dash-prefixed word" (file_test_reset '-y one' kept; file.lines.filter $file_test_path -y >/dev/null; file_test_contents) = 'kept'
@test "fails for a missing file" (file.lines.filter /nonexistent/file alpha 2>/dev/null; echo $status) = 1

rm --force $file_test_path
