# Tests for path.withsuffix. Run with: fishtape ~/.config/fish/tests/path.withsuffix.fish

@test "inserts a suffix before the extension" (path.withsuffix .bak foo.txt) = foo.bak.txt
@test "handles multi-dot names" (path.withsuffix .bak archive.tar.gz) = archive.tar.bak.gz
@test "appends to a name without an extension" (path.withsuffix .bak noext) = noext.bak
@test "handles dotfiles" (path.withsuffix .bak .hidden) = .hidden.bak

@test "--ext replaces the extension" (path.withsuffix --ext .zip .bak foo.txt) = foo.bak.zip
@test "--ext works without a suffix" (path.withsuffix --ext .zip foo.txt) = foo.zip
@test "accepts --ext without a leading dot" (path.withsuffix --ext zip .bak foo.txt) = foo.bak.zip

@test "fails without a suffix or --ext" (path.withsuffix foo.txt 2>/dev/null; echo $status) = 2
@test "prints usage without a suffix or --ext" (path.withsuffix foo.txt 2>&1) = 'Usage: path.withsuffix SUFFIX [--ext EXT] INPUT'
