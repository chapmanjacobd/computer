# Tests for lines.coln. Run with: fishtape ~/.config/fish/tests/lines.coln.fish

@test "selects a positive column" (printf 'a b c\nd e f\n' | lines.coln 2 | string join '|') = 'b|e'
@test "selects the first column" (printf 'a b c\nd e f\n' | lines.coln 1 | string join '|') = 'a|d'
@test "selects from the end with a negative column" (printf 'a b c\nd e f\n' | lines.coln -1 | string join '|') = 'c|f'
@test "selects the second-to-last column" (printf 'a b c\nd e f\n' | lines.coln -2 | string join '|') = 'b|e'
@test "skips blank lines with a negative column" (printf 'a b\n\nc d\n' | lines.coln -1 | string join '|') = 'b|d'
@test "prints nothing for column zero" -z (printf 'a b\n' | lines.coln 0)
