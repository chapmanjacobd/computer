#!/usr/bin/env bash

set -Eeuox pipefail

ssh-keygen -t ed25519 -q -N '' </dev/zero || true
cat .ssh/id_ed25519.pub >> .ssh/authorized_keys
sudo visudo

cat .github/etc/nanorc | sudo tee /etc/nanorc

# sudo -v && wget -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sudo sh /dev/stdin

sudo apt install pipx python-is-python3 eza libguestfs-tools qemu-guest-agent bfs wget2 tmux earlyoom zoxide cargo kitty git-delta progress ncdu fzf fish cmake fonts-noto-color-emoji fd-find

git clone https://github.com/ku1ik/stderred.git
cd stderred
make

sudo systemctl enable --now earlyoom

sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://repo.charm.sh/apt/gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/charm.gpg
echo "deb [signed-by=/etc/apt/keyrings/charm.gpg] https://repo.charm.sh/apt/ * *" | sudo tee /etc/apt/sources.list.d/charm.list
sudo apt update && sudo apt install gum

mkdir -p ~/.ssh/control/
cat ~/.github/etc/ssh/sshd_config.d/10-xk.conf | sudo tee /etc/ssh/sshd_config.d/10-xk.conf

sudo loginctl enable-linger xk
fish -c 'curl -sL https://git.io/fisher | source && fisher install jorgebucaran/fisher (cat ~/.config/fish/fish_plugins)'
chsh -s /usr/bin/fish

pipx install library trash-cli black datasette ipython ipdb isort memray mutmut pytest pycln pur pipdeptree pdm scalene sparseutils sqlite-utils ssort sshuttle torrentool yt-dlp
# library cp --dry-run ~/.github/etc/ /etc/
# sudo cp -a ~/.github/etc/. /etc/

# sudo systemctl enable --now sshd
# sudo systemctl enable --now fstrim.timer
# sudo systemctl enable --now apcupsd

sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
sudo systemctl disable --now systemd-journald-audit.socket
sudo systemctl mask systemd-journald-audit.socket

for dep in $(cat ~/.github/cargo_installed); do
    cargo install $dep
done

cat ~/.github/vscode_extensions.txt | xargs -I{} -n1 code --install-extension {} --force
