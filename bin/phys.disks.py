#!/usr/bin/env python3
import json
import os
import re
import subprocess

BAY_LAYOUT = [
    [0, 3, 6, 9],
    [1, 4, 7, 10],
    [2, 5, 8, 11],
]

SLOT_RE = re.compile(r"pci-0000:03:00.0-scsi-0:0:(\d+):0", re.IGNORECASE)


def load_lsblk():
    out = subprocess.check_output(["lsblk", "-o", "NAME,KNAME,TYPE,MOUNTPOINT,PATH", "--json"])
    return json.loads(out)


def get_dev_bay_map():
    baymap = {i: {"dev": None, "mount": None} for i in range(12)}

    bypath = "/dev/disk/by-path"
    if not os.path.isdir(bypath):
        return baymap

    dev_to_bay = {}

    for entry in os.listdir(bypath):
        full = os.path.join(bypath, entry)

        try:
            real = os.path.realpath(full)
        except:
            continue

        m = SLOT_RE.search(entry)
        if not m:
            continue

        bay = int(m.group(1))
        if 0 <= bay <= 11:
            dev_to_bay[real] = bay

    ls = load_lsblk()

    def walk(node):
        if node["type"] == "disk":
            real = f"/dev/{node['kname']}"

            if real in dev_to_bay:
                bay = dev_to_bay[real]

                mount = None
                for child in node.get("children", []):
                    if isinstance(child, dict) and child.get("mountpoint"):
                        mount = os.path.basename(child["mountpoint"])
                        break

                baymap[bay]["dev"] = node["kname"]
                baymap[bay]["mount"] = mount

        for c in node.get("children", []):
            if isinstance(c, dict):
                walk(c)

    for blk in ls["blockdevices"]:
        walk(blk)

    return baymap


def render_ascii(bays):
    lines = []
    for row in BAY_LAYOUT:
        row_text = []
        for bay in row:
            info = bays[bay]
            dev = info["dev"]
            mount = info["mount"]

            if dev is None:
                text = f"[ ]         "
            elif mount:
                text = f"[!] {dev:<3} {mount:>4}"
            else:
                text = f"[O] {dev:<3}     "

            row_text.append(text)

        lines.append(" | ".join(row_text))

    return "\n".join(lines)


def main():
    bays = get_dev_bay_map()
    print(render_ascii(bays))


if __name__ == "__main__":
    main()
