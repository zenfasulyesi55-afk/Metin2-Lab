import os, re, zipfile
V3 = "metin2_v3_ultrahd_tum_koyler_ve_120aura.zip"
ST = "/tmp/m2stage"

def wt(rel, data, tgts):
    rel = rel.replace("\\", "/").lstrip("/")
    for t in tgts:
        o = os.path.join(t, rel)
        os.makedirs(os.path.dirname(o), exist_ok=True)
        open(o, "wb").write(data)

def loose(roots):
    n = 0
    for r in roots:
        for dp, _, fns in os.walk(r):
            for fn in fns:
                if fn.lower() not in ("userinterface.cpp", "eterpackmanager.cpp"): continue
                p = os.path.join(dp, fn)
                s = open(p, encoding="utf-8", errors="ignore").read()
                ns = s.replace("CEterPackManager::SEARCH_PACK_FIRST", "CEterPackManager::SEARCH_FILE_FIRST")
                ns = re.sub(r'(\bbPackFirst\s*=\s*)true\b', r'\1false', ns)
                if ns != s:
                    open(p, "w", encoding="utf-8").write(ns); n += 1
    print("[P8] LOOSE:", n)

def sync_py(roots, tgts):
    hk = '\n# [P8_AURA120]\ntry:\n    import chrmgr as _c\n    _c.RegisterEffect(_c.EFFECT_AFFECT + 95, "", "d:/ymir work/effect/etc/lvl120_aura/lvl120_gold_aura.mse")\nexcept Exception:\n    pass\n'
    hud = {}
    for r in roots:
        for dp, _, fns in os.walk(r):
            for fn in fns:
                low, p = fn.lower(), os.path.join(dp, fn)
                if low in ("uimobilehud.py", "uidevoptions.py") and "data-overlay" in dp.replace("\\", "/"):
                    s = open(p, encoding="utf-8", errors="ignore").read()
                    if low == "uimobilehud.py" and "[P8_AURA120]" not in s:
                        s = re.sub(r'^[ \t]+', lambda m: m.group(0).replace('\t', '    '), s, flags=re.M) + hk
                        open(p, "w", encoding="utf-8").write(s)
                    hud[low] = s.encode("utf-8")
                elif low == "playersettingmodule.py":
                    s = open(p, encoding="utf-8", errors="ignore").read()
                    if "lvl120_gold_aura.mse" not in s:
                        m = re.search(r'^([ \t]*)chrmgr\.RegisterEffect\s*\(\s*chrmgr\.EFFECT_AFFECT', s, re.M)
                        if m:
                            ins = m.group(1) + 'chrmgr.RegisterEffect(chrmgr.EFFECT_AFFECT + 95, "", "d:/ymir work/effect/etc/lvl120_aura/lvl120_gold_aura.mse")\n'
                            open(p, "w", encoding="utf-8").write(s[:m.start()] + ins + s[m.start():])
                            print("[P8] PY_PSM:", p)
    c = 0
    if os.path.isdir(ST) and hud:
        for dp, _, fns in os.walk(ST):
            for fn in fns:
                if fn.lower() in hud:
                    wt(os.path.relpath(os.path.join(dp, fn), ST), hud[fn.lower()], tgts); c += 1
        if os.path.isdir(os.path.join(ST, "root")):
            for k, v in hud.items(): wt("root/" + k, v, tgts); c += 1
    print("[P8] SYNC_HUD:", c)

def v3(repo, tgts):
    zp = next((c for c in (os.path.join(repo, V3), os.path.join(os.getcwd(), V3)) if os.path.exists(c)), None)
    if not zp: print("[P8] NO_ZIP"); return
    au = ev = dd = st = rp = 0
    envs, kd = {}, {"a": {}, "b": {}, "c": {}}
    with zipfile.ZipFile(zp) as zf:
        for i in zf.infolist():
            if i.is_dir(): continue
            nm = i.filename.replace("\\", "/")
            if "/pack_hazir_yapi/" not in nm.lower(): continue
            sub, dt = nm.split("PACK_HAZIR_YAPI/", 1)[1], zf.read(i)
            low = sub.lower()
            if sub.startswith("effect/ymir work/"): wt(sub[7:], dt, tgts); au += 1
            elif sub.startswith("etc/ymir work/environment/") and low.endswith(".msenv"):
                k = os.path.basename(low)[0]; envs[k] = dt
                wt(sub[4:], dt, tgts); wt(f"ymir work/environment/{k}1.msenv", dt, tgts); wt(f"ymir work/environment/metin2_map_{k}1.msenv", dt, tgts); ev += 1
            elif sub.startswith("zone/ymir work/") and low.endswith(".dds"):
                wt(sub[5:], dt, tgts); dd += 1
                fn = os.path.basename(low); k = fn[0]
                if k in kd:
                    for tag, key in (("cobble","cob"),("carved_stone","stn"),("classic_wood","wd"),("roof","rf")):
                        if tag in fn: kd[k][key] = dt
    skip = ("grass","moss","dirt","mud","sand","water","soil","leaf","tree")
    if os.path.isdir(ST):
        for dp, _, fns in os.walk(ST):
            dl = dp.replace("\\", "/").lower()
            for fn in fns:
                fl, fp = fn.lower(), os.path.join(dp, fn)
                m = re.search(r'metin2_map_([abc])1$', dl)
                if m and fl == "setting.txt" and m.group(1) in envs:
                    k = m.group(1); s = open(fp, encoding="utf-8", errors="ignore").read()
                    em = re.search(r'(?im)^Environment\s+(\S+)', s)
                    if em and em.group(1).lower() != "default.msenv": wt("ymir work/environment/" + em.group(1), envs[k], tgts)
                    ns = re.sub(r'(?im)^Environment\s+\S+', f"Environment\t{k}1_remastered_hd.msenv", s)
                    if ns == s: ns = s.rstrip() + f"\nEnvironment\t{k}1_remastered_hd.msenv\n"
                    wt(os.path.relpath(fp, ST), ns.encode("utf-8"), tgts); st += 1
                tm = re.search(r'metin2_([abc])1\.txt$', fl)
                if tm and "textureset" in dl:
                    k = tm.group(1); s = open(fp, encoding="utf-8", errors="ignore").read()
                    for pm in re.findall(r'"([^"]+\.dds)"', s, re.I):
                        pl = pm.replace("\\", "/").lower()
                        if any(x in pl for x in skip): continue
                        tr = re.sub(r'^[a-z]:/', '', pm.replace("\\", "/"), flags=re.I).lstrip("/")
                        if any(x in pl for x in ("road","way","street","tile","cobble","pave","brick","plaza")) and "cob" in kd[k]: wt(tr, kd[k]["cob"], tgts); rp += 1
                        elif any(x in pl for x in ("stone","rock","block","floor","wall")) and "stn" in kd[k]: wt(tr, kd[k]["stn"], tgts); rp += 1
                km = re.search(r'ymir work/(?:terrainmaps|zone)/([abc])/', dl)
                if km and fl.endswith(".dds") and "_v2" not in dl and not any(x in fl for x in skip):
                    k = km.group(1); pk = None
                    if any(x in fl for x in ("road","way","street","cobble","pave","plaza","brick")): pk = kd[k].get("cob")
                    elif any(x in fl for x in ("roof","giwa","slate")): pk = kd[k].get("rf")
                    elif any(x in fl for x in ("wood","pillar","door","beam","fence","stall")): pk = kd[k].get("wd")
                    elif any(x in fl for x in ("stone","wall","floor","step","stair","bridge")): pk = kd[k].get("stn")
                    if pk: wt(os.path.relpath(fp, ST), pk, tgts); rp += 1
    print(f"[P8] V3 au={au} ev={ev} dd={dd} st={st} rp={rp}")

def run():
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ws = os.path.dirname(repo)
    print("[P8] ST:", " ".join(sorted(os.listdir(ST))[:15]) if os.path.isdir(ST) else "MISSING")
    pf = os.path.join(repo, "patch", "files"); os.makedirs(pf, exist_ok=True)
    tgts = [t for t in (ST, pf) if os.path.isdir(t)]
    roots = [r for r in (os.path.join(ws, "client-src"), os.path.join(repo, "client-src"), ST) if os.path.isdir(r)]
    loose(roots); sync_py(roots, tgts); v3(repo, tgts)

if __name__ == "__main__": run()
