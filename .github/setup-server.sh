#!/usr/bin/env bash

set -Eeuox pipefail

sudo hostnamectl hostname pakon
sudo localectl set-keymap us-colemak_dh

ssh-keygen -t ed25519 -q -N '' </dev/zero || true
cat .ssh/id_ed25519.pub >> .ssh/authorized_keys
sudo visudo

echo -e '127.0.0.1\t' $(hostnamectl | grep -i "static hostname:" | cut -f2- -d:) | sudo tee -a /etc/hosts

cat /home/xk/.github/etc/nanorc | sudo tee /etc/nanorc

# library cp --dry-run ~/.github/etc/ /etc/
# sudo cp -a ~/.github/etc/. /etc/
# sudo restorecon -R /etc
mkdir ~/.ssh/control/
cat ~/.github/etc/ssh/sshd_config.d/10-xk.conf | sudo tee /etc/ssh/sshd_config.d/10-xk.conf
sudo systemctl enable --now sshd
sudo systemctl enable --now fstrim.timer

sudo dnf update -y

sudo dnf install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
sudo dnf install https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm

sudo dnf install --allowerasing ffmpeg python3 python3-pip git android-tools ImageMagick detox dnscrypt-proxy expect fish fzf git-lfs htop inotify-tools jq libpq-devel moreutils ncdu nmon pg_top pspg ripgrep syncthing trash-cli wget dnf-plugins-extras-tracer cpufrequtils postgresql-devel sqlite-devel bash-completion fd-find parallel mkvtoolnix oniguruma-devel libacl-devel libattr-devel libcap-devel btrfsmaintenance dnf-automatic intel-media-driver rpmfusion-free-release-tainted rpmfusion-nonfree-release-tainted moby-engine cargo freerdp-server

sudo dnf groupupdate -y multimedia --setop="install_weak_deps=False" --exclude=PackageKit-gstreamer-plugin
sudo dnf groupupdate -y sound-and-video

sudo systemctl start btrfsmaintenance-refresh
sudo systemctl enable --now dnf-automatic-install.timer

sudo rm /etc/profile.d/which2.sh
sudo loginctl enable-linger xk
chsh -s /bin/fish
fish -c 'curl -sL https://git.io/fisher | source && fisher install jorgebucaran/fisher (cat ~/.config/fish/fish_plugins)'

sudo dnf erase kcalc PackageKit konversation falkon dragon konversation falkon kget ktorrent konqueror chromium autokey kontact dolphin Kontact dolphin kwrite calligra\* korganizer kmail akregator knode krdc krfb konqueror ktnef kaddressbook konversation kf5-akonadi-server mariadb-common kmail kontact akregator dragon kmag kmines kmousetool korganizer kwrite kaddressbook elisa-player gnome-keyring bolt podman

sudo dnf group install -y "C Development Tools and Libraries"
sudo dnf install liburing-devel

cd ~/ && mkdir -p bin/ && cd bin/ && rm -rf bfs/ && git clone https://github.com/tavianator/bfs.git
cd bfs && ./configure --enable-release && make && sudo make install

# flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
# flatpak install flathub org.freedesktop.Platform.ffmpeg-full

for package in (cat ~/.github/dnf_installed)
    sudo dnf install -y $package
end

sudo -v && wget -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sudo sh /dev/stdin

# sudo usermod -aG docker xk
# mkdir -p ~/.docker/cli-plugins/
# curl -SL https://github.com/docker/compose/releases/download/v2.16.0/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
# chmod +x ~/.docker/cli-plugins/docker-compose

sudo systemctl enable --now apcupsd

sudo dnf swap mesa-va-drivers mesa-va-drivers-freeworld
sudo dnf swap mesa-vdpau-drivers mesa-vdpau-drivers-freeworld
#sudo dnf swap mesa-va-drivers.i686 mesa-va-drivers-freeworld.i686
#sudo dnf swap mesa-vdpau-drivers.i686 mesa-vdpau-drivers-freeworld.i686

sudo systemctl mask systemd-oomd
sudo systemctl enable --now earlyoom
sudo systemctl set-default multi-user.target
sudo systemctl disable --now /usr/lib/systemd/system/sysstat-*.timer
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
sudo systemctl disable --now systemd-journald-audit.socket
sudo systemctl mask systemd-journald-audit.socket

# rm -r ~/.local/share/kactivitymanagerd && touch ~/.local/share/kactivitymanagerd && sudo chmod -x /usr/libexec/kactivitymanagerd  # Plasma 6 does not like this...

for dep in $(cat .github/cargo_installed); do
    cargo install $dep
done

sudo wget -O /etc/yum.repos.d/xpra.repo https://raw.githubusercontent.com/Xpra-org/xpra/master/packaging/repos/Fedora/xpra.repo
sudo dnf install -y xpra

# alternatives: https://github.com/wg-easy/wg-easy https://github.com/juanfont/headscale ZeroTier netbird
sudo dnf config-manager --add-repo https://pkgs.tailscale.com/stable/fedora/tailscale.repo
sudo dnf install tailscale

echo 'unqualified-search-registries = ["docker.io"]' | sudo tee /etc/containers/registries.conf

sudo systemctl enable --now tailscaled
echo remember to disable key expiry
sudo tailscale up
tailscale ip -4
# https://major.io/p/build-tailscale-exit-node-firewalld/

sudo systemctl enable --now qbittorrent-nox@xk.service

sudo sed -i 's/compress=zstd:1/noatime,compress=zstd:2/' /etc/fstab

sudo fwupdmgr refresh --force && \
sudo fwupdmgr get-updates && \
sudo fwupdmgr update
