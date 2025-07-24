// cat ~/bin/copyq_clean.js | copyq eval -

var numItems = size();
var thresholdBytes = 1024 * 80;

print(numItems);
print()

for (var i = numItems - 1; i >= 0; i--) {
    var itemContent = read(i);

    if (itemContent && itemContent.length > thresholdBytes) {
        print(itemContent);
        remove(i);
    }
}

print(size());
