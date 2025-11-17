#!/usr/bin/env python3
import json
import os
import subprocess

BAY_LAYOUT = [
    [0, 3, 6, 9],
    [1, 4, 7, 10],
    [2, 5, 8, 11],
]

def load_lsblk():
    out = subprocess.check_output(["lsblk", "-o", "NAME,KNAME,TYPE,MOUNTPOINT,HCTL", "--json"])
    return json.loads(out)

def get_dev_bay_map():
    baymap = {i: {"dev": None, "mount": None} for i in range(12)}
    ls = load_lsblk()
    
    def walk(node):
        if node["type"] == "disk":
            hctl = node.get("hctl", "")
            if hctl:
                parts = hctl.split(":")
                if len(parts) == 4:
                    h, c, t, l = parts
                    bay = int(t)
                    if 0 <= bay <= 11:
                        mount = None
                        for child in node.get("children", []):
                            if isinstance(child, dict) and child.get("mountpoint"):
                                mount = os.path.basename(child["mountpoint"].rstrip(os.sep))
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
                text = f"[\033[32mO\033[0m] {dev:<3}     "
            row_text.append(text)
        lines.append(" | ".join(row_text))
    return "\n".join(lines)

def main():
    bays = get_dev_bay_map()
    print(render_ascii(bays))

if __name__ == "__main__":
    main()
