#!/usr/bin/env bash

set -Eeuox pipefail

ssh-keygen -t ed25519 -q -N '' </dev/zero || true
sudo visudo

sudo cp -a ~/.github/etc/. /etc/ && sudo restorecon -R /etc
sudo systemctl enable --now sshd
sudo systemctl enable --now fstrim.timer

sudo dnf update -y

sudo dnf install --allowerasing ffmpeg python3 python3-pip git android-tools ImageMagick detox dnscrypt-proxy expect fish fzf git-lfs htop inotify-tools jq libpq-devel moreutils ncdu nmon pg_top pspg ripgrep syncthing trash-cli wget dnf-plugins-extras-tracer cpufrequtils postgresql-devel sqlite-devel bash-completion fd-find parallel mkvtoolnix oniguruma-devel libacl-devel libattr-devel libcap-devel btrfsmaintenance dnf-automatic intel-media-driver rpmfusion-free-release-tainted rpmfusion-nonfree-release-tainted moby-engine

sudo dnf groupupdate -y multimedia --setop="install_weak_deps=False" --exclude=PackageKit-gstreamer-plugin
sudo dnf groupupdate -y sound-and-video

sudo systemctl start btrfsmaintenance-refresh
sudo systemctl enable --now dnf-automatic-install.timer

sudo loginctl enable-linger xk
chsh -s /bin/fish
fish -c 'curl -sL https://git.io/fisher | source && fisher install jorgebucaran/fisher (cat ~/.config/fish/fish_plugins)'

sudo dnf erase kcalc PackageKit konversation falkon dragon konversation falkon kget ktorrent konqueror chromium autokey kontact dolphin Kontact dolphin kwrite calligra* korganizer kmail akregator knode krdc krfb konqueror ktnef kaddressbook konversation kf5-akonadi-server mariadb-common kmail kontact akregator dragon kmag kmahjongg kmines kmousetool korganizer kwrite kaddressbook elisa-player gnome-keyring

cd ~/ && mkdir -p bin/ && cd bin/ && rm -rf bfs/ && git clone https://github.com/tavianator/bfs.git
cd bfs && make release && sudo make install

flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak install flathub org.freedesktop.Platform.ffmpeg-full

sudo dnf install $(cat ~/.github/dnf_installed)

sudo dnf swap mesa-va-drivers mesa-va-drivers-freeworld
sudo dnf swap mesa-vdpau-drivers mesa-vdpau-drivers-freeworld
#sudo dnf swap mesa-va-drivers.i686 mesa-va-drivers-freeworld.i686
#sudo dnf swap mesa-vdpau-drivers.i686 mesa-vdpau-drivers-freeworld.i686

sudo systemctl mask systemd-oomd
sudo systemctl set-default multi-user.target
