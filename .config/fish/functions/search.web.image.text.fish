function search.web.image.text
    google-chrome https://www.pexels.com/search/"$argv"

    google-chrome https://unsplash.com/search/photos/"$argv"

    google-chrome https://pixabay.com/en/photos/"$argv"

    google-chrome 'https://www.flickr.com/search/?text='"$argv"'&license=7%2C9%2C10&sort=date-taken-desc'

    google-chrome https://stocksnap.io/search/"$argv"
end
