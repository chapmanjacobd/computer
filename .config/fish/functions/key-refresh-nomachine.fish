# Defined via `source`
function key-refresh-nomachine -a label
    set oldkey (mktemp --tmpdir=/home/xk/.ssh/old/ id_rsa_nx_XXXXX)
    mv ~/.ssh/id_rsa_nx $oldkey
    mv ~/.ssh/id_rsa_nx.pub $oldkey.pub

    ssh-keygen -t rsa -C $label -q -N '' -f ~/.ssh/id_rsa_nx </dev/zero || true
    cat ~/.ssh/id_rsa_nx.pub >>~/.nx/config/authorized.crt
    filterfile ~/.nx/config/authorized.crt (cat $oldkey.pub)
end
