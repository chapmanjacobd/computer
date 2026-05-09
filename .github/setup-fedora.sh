#!/usr/bin/env bash

set -Eeuox pipefail

#source "${BASH_SOURCE%/setup-server.sh}"
sudo systemctl set-default graphical.target

sudo dnf swap mesa-va-drivers mesa-va-drivers-freeworld || true
sudo dnf swap mesa-vdpau-drivers mesa-vdpau-drivers-freeworld || true
#sudo dnf swap mesa-va-drivers.i686 mesa-va-drivers-freeworld.i686
#sudo dnf swap mesa-vdpau-drivers.i686 mesa-vdpau-drivers-freeworld.i686

# fpsync /home/xk/ 192.168.68.65:/home/xk/
# fpsync /mnt/d/ 192.168.68.65:/mnt/d/

sudo dnf group install core -y
sudo dnf install -y gstreamer1-plugins-{bad-\*,good-\*,base} gstreamer1-plugin-openh264 gstreamer1-libav --exclude=gstreamer1-plugins-bad-free-devel
sudo dnf install -y lame\* --exclude=lame-devel

curl https://zed.dev/install.sh | sh

sudo dnf update
sudo dnf install -y mpv ffmpeg python3 python3-pip git android-tools R ImageMagick bat copyq darktable java-latest-openjdk detox cowsay dnscrypt-proxy evince expect fdk-aac fdupes fish gdal fzf gdal-devel ffmpeg-devel gdal-java geos-devel gdal-python-tools gimp git-delta git-lfs htop inotify-tools jq kdiff3 keepassxc kitty krename lato-fonts libpq-devel libreoffice mediawriter meld moreutils ncdu nmon nomacs pg_top picard plasma-workspace-x11 podman-docker pspg python3-qgis ripgrep syncthing udunits2 wine xdotool xclip xbacklight trash-cli wget fedora-workstation-repositories dnf-plugins-extras-tracer cpufrequtils postgresql-devel breeze-gtk gdal-devel sqlite-devel bash-completion fd-find krusader xmodmap sxhkd xsel xinput kcron parallel mkvtoolnix oniguruma-devel libacl-devel libattr-devel libcap-devel btrfsmaintenance ddcutil dnf-automatic xset rmlint skanpage mpv-mpris

#setxkbmap us -variant altgr-intl -option caps:backspace

sudo dnf erase kcalc PackageKit konversation falkon dragon konversation falkon kget ktorrent konqueror docker autokey kontact dolphin Kontact dolphin kwrite calligra* korganizer kmail akregator knode krdc krfb konqueror ktnef kaddressbook konversation kf5-akonadi-server mariadb-common kmail kontact akregator dragon kmag kmines kmousetool korganizer kwrite kaddressbook elisa-player gnome-keyring ksshaskpass
# sudo dnf erase plasma-discover

# sudo systemctl unmask sleep.target suspend.target hibernate.target hybrid-sleep.target

python -m ensurepip
python -m pip install --upgrade pip
for dep in $(cat .github/pip_installed); do
    python -m pip install $dep
done
python -m pip install yt-dlp pipenv catt library

#rsync -ah --info=progress2 --no-inc-recursive /run/media/xk/backup/xk/ ~/
cd ~ && sudo restorecon -vR .
#reboot
R --slave -e 'update.packages()'

# sudo podman-compose systemd -a create-unit
