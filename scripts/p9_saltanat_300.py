#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glob, os, re, shutil, subprocess, sys

SALTANAT_REPO = "https://github.com/MaviRuh13/saltanat-files.git"
SALTANAT_DIR = "/tmp/saltanat"
STAGE_DIR = "/tmp/m2stage"
SERVER_SRC = "/tmp/m2dev-server-src"
SERVER_PACK = "/tmp/m2serverpack"
CLIENT_ROOT = "client-src/r10dev.net OPENGL-ITJA"

ALLOWED_EXT = (
    ".gr2", ".dds", ".tga", ".mse", ".msa", ".msm",
    ".mde", ".jpg", ".png", ".txt", ".sub", ".atr", ".mdatr"
)
ASSET_PACKS = ("models", "pets", "mounts", "effects", "npcs", "monsters")
MAP_ENVS = {
    "metin2_map_a1": "A1.msenv",
    "metin2_map_b1": "B1.msenv",
    "metin2_map_c1": "C1.msenv",
}

def _sub_file(fp, rules, dry=False):
    if not os.path.isfile(fp):
        return (False, "YOK")
    orig = open(fp, encoding="utf-8", errors="ignore").read()
    cur = orig
    hits = 0
    for pat, rep in rules:
        cur, n = re.subn(pat, rep, cur, flags=re.M | re.S)
        hits += n
    if not dry and cur != orig:
        open(fp, "w", encoding="utf-8").write(cur)
    return (hits > 0, f"{hits}x")

def _patch_struct_field(fp, struct_name, field_pat, rep, dry=False):
    if not os.path.isfile(fp):
        return (False, "YOK")
    orig = open(fp, encoding="utf-8", errors="ignore").read()
    pat = rf'(struct\s+{struct_name}\b[^{{]*\{{[^}}]*?)({field_pat})'
    cur, n = re.subn(pat, rf'\1{rep}', orig, count=1, flags=re.S)
    if not dry and cur != orig:
        open(fp, "w", encoding="utf-8").write(cur)
    return (n > 0, f"{n}x")

def _patch_exp_tables(fp, dry=False):
    if not os.path.isfile(fp):
        return (False, "YOK")
    orig = open(fp, encoding="utf-8", errors="ignore").read()
    count = 0
    def repl(m):
        nonlocal count
        head, body = m.group(1), m.group(2)
        nums = re.findall(r'\b\d+\b', re.sub(r'//[^\n]*|/\*.*?\*/', '', body, flags=re.S))
        if len(nums) < 301:
            nums = nums + ["2100000000"] * (301 - len(nums))
        count += 1
        lines = []
        for i in range(0, len(nums), 5):
            lines.append("\t" + ", ".join(nums[i:i+5]) + ",")
        return head + "\n" + "\n".join(lines) + "\n};"
    pat = r'(const\s+\w+\s+exp_table\w*\[\s*PLAYER_EXP_TABLE_MAX\s*\+\s*1\s*\]\s*=\s*\{)([^}]+)\};'
    cur = re.sub(pat, repl, orig, flags=re.S)
    if not dry and cur != orig:
        open(fp, "w", encoding="utf-8").write(cur)
    return (count > 0, f"{count}tablo")

def patch_core_300(srv_root=SERVER_SRC, cli_root=CLIENT_ROOT, dry=False):
    res = []
    res.append(("SRV length.h", _sub_file(f"{srv_root}/src/common/length.h", [
        (r'PLAYER_EXP_TABLE_MAX\s*=\s*\d+', 'PLAYER_EXP_TABLE_MAX = 300'),
        (r'PLAYER_MAX_LEVEL_CONST\s*=\s*\d+', 'PLAYER_MAX_LEVEL_CONST = 300'),
    ], dry)))
    res.append(("SRV SSimplePlayer", _patch_struct_field(
        f"{srv_root}/src/common/tables.h", "SSimplePlayer",
        r'\b(?:uint8_t|BYTE|int)\s+byLevel\s*;', 'int byLevel;', dry)))
    res.append(("SRV SPlayerTable", _patch_struct_field(
        f"{srv_root}/src/common/tables.h", "SPlayerTable",
        r'\b(?:uint8_t|BYTE|int)\s+level\s*;', 'int level;', dry)))
    res.append(("SRV char.h", _sub_file(f"{srv_root}/src/game/char.h", [
        (r'(\b(?:BYTE|uint8_t|int)\s+)level\s*;', 'int level;'),
        (r'void\s+SetLevel\s*\(\s*(?:BYTE|uint8_t|int)\s+level\s*\)', 'void SetLevel(int level)'),
    ], dry)))
    res.append(("SRV char.cpp", _sub_file(f"{srv_root}/src/game/char.cpp", [
        (r'void\s+CHARACTER::SetLevel\s*\(\s*(?:BYTE|uint8_t|int)\s+level\s*\)', 'void CHARACTER::SetLevel(int level)'),
    ], dry)))
    res.append(("SRV config.cpp", _sub_file(f"{srv_root}/src/game/config.cpp", [
        (r'int\s+gPlayerMaxLevel\s*=\s*\d+\s*;', 'int gPlayerMaxLevel = 300;'),
    ], dry)))
    res.append(("SRV constants.cpp", _patch_exp_tables(f"{srv_root}/src/game/constants.cpp", dry)))

    pkts = glob.glob(f"{cli_root}/**/Packet.h", recursive=True) + glob.glob(f"{cli_root}/**/packet.h", recursive=True)
    if pkts:
        res.append(("CLI Packet.h", _patch_struct_field(
            pkts[0], "SSimplePlayerInformation",
            r'\b(?:BYTE|uint8_t|int)\s+byLevel\s*;', 'int byLevel;', dry)))
    else:
        res.append(("CLI Packet.h", (False, "YOK")))

    if not dry and os.path.isdir(SERVER_PACK):
        cfg_n = 0
        for r, _, fs in os.walk(SERVER_PACK):
            for f in fs:
                if f == "CONFIG":
                    fp = os.path.join(r, f)
                    t = open(fp, encoding="utf-8", errors="ignore").read()
                    if "MAX_LEVEL" in t:
                        t = re.sub(r'MAX_LEVEL\s*:\s*\d+', 'MAX_LEVEL: 300', t)
                    else:
                        t = t.rstrip() + "\nMAX_LEVEL: 300\n"
                    open(fp, "w", encoding="utf-8").write(t)
                    cfg_n += 1
        res.append(("SRV CONFIG", (cfg_n > 0, f"{cfg_n}x")))
    return res

def ensure_saltanat_repo():
    if not os.path.isdir(SALTANAT_DIR):
        subprocess.check_call(["git", "clone", "--depth", "1", SALTANAT_REPO, SALTANAT_DIR])

def sync_saltanat_assets():
    if not os.path.isdir(STAGE_DIR):
        print("[p9] m2stage yok, varlik kopyalama atlandi")
        return 0
    copied = 0
    for pack in ASSET_PACKS:
        base = os.path.join(SALTANAT_DIR, pack)
        if not os.path.isdir(base):
            continue
        for sub in ("ymir work", "icon"):
            src_root = os.path.join(base, sub)
            if not os.path.isdir(src_root):
                continue
            for r, _, fs in os.walk(src_root):
                rel = os.path.relpath(r, base)
                dst_dir = os.path.join(STAGE_DIR, rel)
                os.makedirs(dst_dir, exist_ok=True)
                for f in fs:
                    fl = f.lower()
                    if fl == "thumbs.db" or not fl.endswith(ALLOWED_EXT):
                        continue
                    shutil.copy2(os.path.join(r, f), os.path.join(dst_dir, f))
                    copied += 1
    print(f"[p9] Saltanat varliklari eklendi: {copied}")
    return copied

def fix_skybox_maps():
    if not os.path.isdir(STAGE_DIR):
        return
    fixed = 0
    for r, _, fs in os.walk(STAGE_DIR):
        bn = os.path.basename(r).lower()
        if bn in MAP_ENVS and "setting.txt" in fs:
            p = os.path.join(r, "setting.txt")
            lines = open(p, encoding="utf-8", errors="ignore").read().splitlines()
            lines = [l for l in lines if not l.strip().lower().startswith("environment")]
            lines.append(f"Environment\t\t{MAP_ENVS[bn]}")
            open(p, "w", encoding="utf-8").write("\n".join(lines) + "\n")
            fixed += 1
    print(f"[p9] Skybox setting.txt onarildi: {fixed}")

def run():
    print("=== [P9] SALTANAT 300 OVERHAUL ===")
    ensure_saltanat_repo()
    for name, (ok, info) in patch_core_300(dry=False):
        print(f"  [{'OK' if ok else '!!'}] {name}: {info}")
    sync_saltanat_assets()
    fix_skybox_maps()

if __name__ == "__main__":
    if "--check" in sys.argv:
        cli = "/tmp/m2check_cli/r10dev.net OPENGL-ITJA"
        print("=== P9 300 LVL DRY-RUN ===")
        for name, (ok, info) in patch_core_300(SERVER_SRC, cli, dry=True):
            print(f"[{'OK' if ok else '!!'}] {name[:18]:18} {info}")
        print("\n=== BYLEVEL KULLANIMI ===")
        for tag, root in [("SRV", f"{SERVER_SRC}/src/db"), ("CLI", cli)]:
            hits = []
            for r, _, fs in os.walk(root):
                for f in fs:
                    if f.endswith((".cpp", ".h")):
                        for l in open(os.path.join(r, f), encoding="utf-8", errors="ignore"):
                            if "byLevel" in l and any(k in l for k in ("str_to_number", "SLOT_LEVEL", "players[")):
                                hits.append(f"{f[:14]}:{l.strip()[:22]}")
            for h in hits[:3]:
                print(f" {tag} {h}")
    else:
        run()
