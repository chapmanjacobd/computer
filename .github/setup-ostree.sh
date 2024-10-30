#!/usr/bin/env bash

set -Eeuox pipefail

read -p "Enter the desired hostname: " desired_hostname
if [ -z "$desired_hostname" ]; then
    echo "Error: Hostname cannot be empty."
    exit 1
fi

sudo hostnamectl hostname $desired_hostname
sudo localectl set-keymap us-colemak_dh

ssh-keygen -t ed25519 -q -N '' </dev/zero || true
cat .ssh/id_ed25519.pub >> .ssh/authorized_keys
sudo visudo

echo -e '127.0.0.1\t' $(hostnamectl | grep -i "static hostname:" | cut -f2- -d:) | sudo tee -a /etc/hosts

cat /home/xk/.github/etc/nanorc | sudo tee /etc/nanorc

# library cp --dry-run ~/.github/etc/ /etc/
# sudo cp -a ~/.github/etc/. /etc/
# !! do not run restorecon  https://bugzilla.redhat.com/show_bug.cgi?id=1259018
mkdir ~/.ssh/control/
cat ~/.github/etc/ssh/sshd_config.d/10-xk.conf | sudo tee /etc/ssh/sshd_config.d/10-xk.conf
sudo systemctl enable --now sshd
sudo systemctl enable --now fstrim.timer

sudo mkdir -p /etc/systemd/logind.conf.d
sudo tee /etc/systemd/logind.conf.d/99-custom-lid.conf <<EOF
[Login]
HandleLidSwitch=ignore
HandleLidSwitchExternalPower=ignore
HandleLidSwitchDocked=ignore
EOF
sudo systemctl daemon-reload
sudo systemctl restart systemd-logind

sudo rpm-ostree upgrade

echo AutomaticUpdatePolicy=apply | sudo tee -a /etc/rpm-ostreed.conf
sudo rpm-ostree reload
sudo systemctl edit --force --full rpm-ostreed-automatic.timer  # change to 3 days
sudo systemctl enable rpm-ostreed-automatic.timer --now
rpm-ostree status

sudo rpm-ostree install https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
sudo systemctl reboot

sudo rpm-ostree override remove firefox firefox-langpacks krfb krfb-libs akonadi-server akonadi-server-mysql mariadb-server mariadb-common kwrite bolt plasma-thunderbolt dolphin dolphin-plugins mariadb-gssapi-server mariadb-errmsg mariadb mariadb-cracklib-password-check mariadb-backup mesa-va-drivers

sudo ostree remote add tailscale https://pkgs.tailscale.com/stable/fedora/tailscale.repo
# TODO: move most of these to flatpaks
sudo rpm-ostree install tailscale fish fzf zoxide tmux exa kitty ffmpeg python3-pip git android-tools detox dnscrypt-proxy expect git-lfs htop inotify-tools libpq-devel moreutils ncdu nmon pg_top pspg ripgrep syncthing trash-cli postgresql-devel sqlite-devel fd-find parallel mkvtoolnix oniguruma-devel libacl-devel libattr-devel libcap-devel btrfsmaintenance intel-media-driver rpmfusion-free-release-tainted rpmfusion-nonfree-release-tainted cargo git-delta lm_sensors go-lang distrobox bfs earlyoom libavcodec-freeworld ffmpegthumbnailer heif-pixbuf-loader libheif-freeworld libheif-tools
sudo rpm-ostree install mesa-va-drivers-freeworld.x86_64 mesa-vdpau-drivers-freeworld.x86_64

sudo rpm-ostree install https://github.com/charmbracelet/gum/releases/download/v0.14.5/gum-0.14.5-1.x86_64.rpm

sudo rpm-ostree install gstreamer1-plugin-libav gstreamer1-plugins-bad-free-extras gstreamer1-plugins-bad-freeworld gstreamer1-plugins-ugly gstreamer1-vaapi
sudo rpm-ostree override remove libavcodec-free libavfilter-free libavformat-free libavutil-free libpostproc-free libswresample-free libswscale-free --install ffmpeg

sudo rpm-ostree update --uninstall rpmfusion-free-release --uninstall rpmfusion-nonfree-release --install rpmfusion-free-release --install rpmfusion-nonfree-release

sudo systemctl reboot

fish -c 'curl -sL https://git.io/fisher | source && fisher install jorgebucaran/fisher (cat ~/.config/fish/fish_plugins)'
sudo rm /etc/profile.d/which2.sh
sudo chsh xk --shell /bin/fish
sudo loginctl enable-linger xk

sudo systemctl start btrfsmaintenance-refresh

sudo systemctl enable --now tailscaled
echo remember to disable key expiry
sudo tailscale up
tailscale ip -4

sudo systemctl mask systemd-oomd
sudo systemctl enable --now earlyoom
sudo systemctl set-default multi-user.target
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target

sudo flatpak remote-delete fedora
flatpak remote-delete fedora

flatpak remote-modify --user --enable flathub || flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo

flatpak update
flatpak install --user -y flathub org.mozilla.firefox
flatpak install --user -y flathub org.libreoffice.LibreOffice
flatpak install --user -y flathub com.github.tchx84.Flatseal
flatpak install --user -y flathub org.freedesktop.Platform.GStreamer.gstreamer-vaapi/x86_64/23.08
flatpak install --user -y flathub org.freedesktop.Platform.ffmpeg-full/x86_64/24.08

for dep in $(cat .github/cargo_installed); do
    cargo install $dep
done

sudo sed -i 's/compress=zstd:1/noatime,compress=zstd:2/' /etc/fstab

sudo fwupdmgr refresh --force && \
sudo fwupdmgr get-updates && \
sudo fwupdmgr update

distrobox create
distrobox enter my-distrobox
