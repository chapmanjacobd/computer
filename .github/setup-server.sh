#!/usr/bin/env bash

set -Eeuox pipefail

ssh-keygen -t ed25519 -q -N '' </dev/zero || true
sudo visudo

sudo cp ~/.github/etc/ssh/xk.conf /etc/ssh/sshd_config.d/
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDBCOUSX1aKXsPdKlBPcy6Gh2ijMH6PeBoE3URiyyWZs xk" >> ~/.ssh/authorized_keys
sudo systemctl enable --now sshd
sudo systemctl enable --now fstrim.timer

sudo dnf update -y

sudo dnf install --allowerasing ffmpeg python3 python3-pip git android-tools ImageMagick detox dnscrypt-proxy expect fish fzf git-lfs htop inotify-tools jq libpq-devel moreutils ncdu nmon pg_top podman-docker pspg ripgrep syncthing trash-cli wget dnf-plugins-extras-tracer cpufrequtils postgresql-devel sqlite-devel bash-completion fd-find parallel mkvtoolnix oniguruma-devel libacl-devel libattr-devel libcap-devel btrfsmaintenance dnf-automatic

sudo systemctl start btrfsmaintenance-refresh
sudo systemctl enable --now dnf-automatic-install.timer

sudo loginctl enable-linger xk
chsh -s /bin/fish

sudo dnf erase kcalc PackageKit konversation falkon dragon konversation falkon kget ktorrent konqueror chromium docker autokey kontact dolphin Kontact dolphin kwrite calligra* korganizer kmail akregator knode krdc krfb konqueror ktnef kaddressbook konversation kf5-akonadi-server mariadb-common kmail kontact akregator dragon kmag kmahjongg kmines kmousetool korganizer kwrite kaddressbook elisa-player gnome-keyring

cd ~/ && mkdir -p bin/ && cd bin/ && rm -rf bfs/ && git clone https://github.com/tavianator/bfs.git
cd bfs && make release && sudo make install

sudo dnf install (cat ~/.github/dnf_installed)
sudo systemctl set-default multi-user.target
curl -sL https://git.io/fisher | source && fisher install jorgebucaran/fisher (cat ~/.config/fish/fish_plugins)

