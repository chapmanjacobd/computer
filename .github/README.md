# computer

if you wanna be my lover you gotta get with my friends:

- [cb](https://github.com/niedzielski/cb)
- [move lines of text](https://github.com/chapmanjacobd/computer/blob/main/.config/fish/functions/lines.mv.fish)
- [filter file](https://github.com/chapmanjacobd/computer/blob/main/.config/fish/functions/file.lines.filter.fish)
- [phone](https://github.com/chapmanjacobd/phone)

## Setup

    cd $HOME
    git clone --no-checkout https://github.com/chapmanjacobd/computer
    mv computer/.git/ .
    rmdir computer

    # mi casa, su casa? sin casa: this will delete everything in your home folder
    #git checkout --force
    #git clean -fd
    # or do this to keep your local versions of conflicts
    git reset
    git ls-files -z --deleted | xargs -0 git checkout --

    bash .github/setup-server.sh
    bash .github/setup-fedora.sh
