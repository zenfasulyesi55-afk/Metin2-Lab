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


def patch_saltanat_ui():
    if not os.path.isdir(STAGE_DIR):
        return
    n = 0
    for r, _, fs in os.walk(STAGE_DIR):
        for f in fs:
            if f.lower() != "uitooltip.py":
                continue
            fp = os.path.join(r, f)
            s = open(fp, encoding="utf-8", errors="ignore").read()
            orig = s
            s = re.sub(r"SPECIAL_POSITIVE_COLOR\s*=\s*grp\.GenerateColor\([^)]+\)",
                "SPECIAL_POSITIVE_COLOR = grp.GenerateColor(0.0, 0.75, 1.0, 1.0)", s, count=1)
            s = re.sub(r"SPECIAL_POSITIVE_COLOR2\s*=\s*grp\.GenerateColor\([^)]+\)",
                "SPECIAL_POSITIVE_COLOR2 = grp.GenerateColor(0.8824, 0.9804, 0.8824, 1.0)", s, count=1)
            c_time = "grp.GenerateColor(1.0, 0.513725, 0.003922, 1.0))"
            s = s.replace("localeInfo.SecondToDHM(restSecond), self.NORMAL_COLOR)",
                f"localeInfo.SecondToDHM(restSecond), {c_time}")
            s = s.replace("localeInfo.SecondToDHM(leftSec), self.NORMAL_COLOR)",
                f"localeInfo.SecondToDHM(leftSec), {c_time}")
            if s != orig:
                open(fp, "w", encoding="utf-8").write(s)
                n += 1
    print(f"[p9] Saltanat UI: {n}")

def patch_saltanat_lists():
    if not os.path.isdir(STAGE_DIR):
        return
    npcs = [("34001","pet_demon_1"),("34002","pet_demon_2"),("34003","pet_demon_3"),
            ("34004","pet_demon_4"),("34005","pet_demon_5"),("20240","plechi_bonedragon_mount"),
            ("20400","drakman"),("6401","fire_dragon2"),("6402","minoking"),
            ("6403","naga_mob_03"),("6404","naga_mob_04")]
    nc = 0
    for r, _, fs in os.walk(STAGE_DIR):
        for f in fs:
            if f.lower() == "npclist.txt":
                fp = os.path.join(r, f)
                s = open(fp, encoding="utf-8", errors="ignore").read()
                add = [f"{v}\t{m}" for v, m in npcs if f"\t{m}" not in s]
                if add:
                    open(fp, "a", encoding="utf-8").write("\n" + "\n".join(add) + "\n")
                    nc += len(add)
    wd = os.path.join(SALTANAT_DIR, "models/ymir work/item/weapon")
    id_ = os.path.join(SALTANAT_DIR, "models/icon/item")
    ws = sorted(f for f in os.listdir(wd) if f.lower().endswith(".gr2")) if os.path.isdir(wd) else []
    ics = sorted(f for f in os.listdir(id_) if f.lower().endswith(".tga")) if os.path.isdir(id_) else []
    ic = 0
    if ws and ics:
        for r, _, fs in os.walk(STAGE_DIR):
            for f in fs:
                if f.lower() == "item_list.txt":
                    fp = os.path.join(r, f)
                    s = open(fp, encoding="utf-8", errors="ignore").read()
                    rows = []
                    for i, wf in enumerate(ws):
                        vn = str(95000 + i)
                        if f"\n{vn}\t" not in s:
                            rows.append(f"{vn}\tWEAPON\ticon/item/{ics[i % len(ics)]}\td:/ymir work/item/weapon/{wf}")
                    if rows:
                        open(fp, "a", encoding="utf-8").write("\n" + "\n".join(rows) + "\n")
                        ic += len(rows)
    print(f"[p9] Listeler: npc={nc}, silah={ic}")


def patch_saltanat_server():
    if not os.path.isdir(SERVER_PACK):
        return
    mobs = [
        ("34001","Demon Pet I",True),("34002","Demon Pet II",True),
        ("34003","Demon Pet III",True),("34004","Demon Pet IV",True),
        ("34005","Demon Pet V",True),("20240","Ejderha Binegi",True),
        ("20400","Drakman Saltanat",True),("6401","Ates Ejderi",False),
        ("6402","Mino Krali",False),("6403","Naga Savasci",False),
        ("6404","Naga Lideri",False),
    ]
    mc = ic = nc = 0
    for r, _, fs in os.walk(SERVER_PACK):
        for f in fs:
            fl = f.lower()
            fp = os.path.join(r, f)
            if fl == "mob_proto.txt":
                ls = open(fp, encoding="utf-8", errors="ignore").read().splitlines()
                raw = "\n".join(ls)
                t_npc = next((l for l in ls if l.startswith(("9003\t","20001\t"))), None)
                t_bos = next((l for l in ls if l.startswith(("691\t","101\t"))), t_npc)
                add = []
                for v, nm, is_n in mobs:
                    if f"\n{v}\t" in raw or raw.startswith(f"{v}\t"): continue
                    base = (t_npc if is_n else t_bos)
                    if not base: continue
                    cs = base.split("\t")
                    cs[0] = v
                    if len(cs) > 1: cs[1] = nm
                    add.append("\t".join(cs))
                if add:
                    open(fp, "a", encoding="utf-8").write("\n" + "\n".join(add) + "\n")
                    mc += len(add)
            elif fl == "mob_names.txt":
                s = open(fp, encoding="utf-8", errors="ignore").read()
                add = [f"{v}\t{nm}" for v, nm, _ in mobs if f"\n{v}\t" not in s]
                if add: open(fp, "a", encoding="utf-8").write("\n" + "\n".join(add) + "\n")
            elif fl == "item_proto.txt":
                ls = open(fp, encoding="utf-8", errors="ignore").read().splitlines()
                raw = "\n".join(ls)
                t_w = next((l for l in ls if l.startswith(("299\t","19\t"))), None)
                add = []
                if t_w:
                    for i in range(24):
                        v = str(95000 + i)
                        if f"\n{v}\t" in raw: continue
                        cs = t_w.split("\t")
                        cs[0] = v
                        if len(cs) > 1: cs[1] = f"Saltanat Silahi +{i+1}"
                        add.append("\t".join(cs))
                if add:
                    open(fp, "a", encoding="utf-8").write("\n" + "\n".join(add) + "\n")
                    ic += len(add)
            elif fl == "item_names.txt":
                s = open(fp, encoding="utf-8", errors="ignore").read()
                add = [f"{95000+i}\tSaltanat Silahi +{i+1}" for i in range(24) if f"\n{95000+i}\t" not in s]
                if add: open(fp, "a", encoding="utf-8").write("\n" + "\n".join(add) + "\n")
        bn = os.path.basename(r)
        coords = {"metin2_map_a1":(651,586),"metin2_map_b1":(637,644),"metin2_map_c1":(387,644)}
        if bn in coords and "npc.txt" in fs:
            fp = os.path.join(r, "npc.txt")
            s = open(fp, encoding="utf-8", errors="ignore").read()
            if "20400" not in s:
                x, y = coords[bn]
                open(fp, "a", encoding="utf-8").write(f"\nm\t{x}\t{y}\t0\t0\t0\t1\t1m\t100\t1\t20400\n")
                nc += 1
    print(f"[p9] Server proto: mob={mc}, item={ic}, drakman={nc}")

def run():
    print("=== [P9] SALTANAT 300 OVERHAUL ===")
    ensure_saltanat_repo()
    for name, (ok, info) in patch_core_300(dry=False):
        print(f"  [{'OK' if ok else '!!'}] {name}: {info}")
    sync_saltanat_assets()
    fix_skybox_maps()
    patch_saltanat_ui()
    patch_saltanat_lists()
    patch_saltanat_server()

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
