import os, re
SRC, PACK = "/tmp/m2dev-server-src", "/tmp/m2serverpack"
GRD = {"metin2_map_a1": ("11000",647,582), "metin2_map_b1": ("11002",633,640), "metin2_map_c1": ("11004",383,640)}
NPCS = [9003, 9001, 9002, 9005, 20016, 9006, 9009]
OX_TR = [
    ("Metin2 oyununda uc farkli krallik bulunur.", True),
    ("Asker At seviyesi en fazla 21 olabilir.", True),
    ("Zehir Kilici 75. seviyede giyilen bir silahtir.", True),
    ("Siyah Celik Zirh sadece Sura sinifina ozeldir.", False),
    ("Dolunay Kilici 30. seviyede kullanilabilir.", True),
    ("Seytan Kulesi toplam 9 kattan olusur.", True),
    ("Demirci esya basarken hicbir zaman esya yakmaz.", False),
    ("At Cagirma P seviyesinde yuzde 100 basarilidir.", True),
    ("Mavi Bayrak kralliginin adi Jinno olarak bilinir.", True),
    ("Sari Bayrak kralliginin adi Chunjo olarak bilinir.", True),
    ("Azrail bossu Seytan Kulesi en ust katinda cikar.", True),
    ("Mavi Iksir karakterin SP degerini yeniler.", True),
    ("Kirmizi Iksir karakterin SP degerini yeniler.", False),
    ("Beran-Setaou Surgun Magarasi bas patronudur.", True),
    ("Bedensel Savasci sinifinda Hava Kilici bulunur.", True),
    ("Zihinsel Savasci sinifinda Guclu Beden bulunur.", True),
    ("Kutsama Kagidi esyanin yok olmasini engeller.", True),
]
def patch_plaza_npcs():
    for r, _, fs in os.walk(PACK):
        f = os.path.basename(r)
        if "npc.txt" not in fs or f not in GRD: continue
        gv, gx, gy = GRD[f]; p = os.path.join(r, "npc.txt")
        raw = open(p, "rb").read().decode("latin1")
        if "# MIKO_PLAZA_NPCS_V1" in raw: continue
        for ln in raw.splitlines():
            ps = ln.split()
            if len(ps) >= 11 and ps[0] == "m" and ps[10] == gv:
                try: gx, gy = int(ps[1]), int(ps[2])
                except: pass
                break
        sx = gx - ((len(NPCS) - 1) * 3) // 2
        add = ["", "# MIKO_PLAZA_NPCS_V1"] + [f"m\t{sx+i*3}\t{gy+6}\t0\t0\t0\t1\t1m\t100\t1\t{v}" for i, v in enumerate(NPCS)]
        open(p, "wb").write((raw.rstrip("\r\n") + "\n" + "\n".join(add) + "\n").encode("latin1"))
def patch_horse_cpp():
    if not os.path.isdir(SRC): return
    ch_h, tgt = "", None
    for r, _, fs in os.walk(SRC):
        if "char.h" in fs and "game" in r.replace("\\", "/"): ch_h = open(os.path.join(r, "char.h"), errors="ignore").read()
        if "input_login.cpp" in fs: tgt = os.path.join(r, "input_login.cpp")
    if not tgt: return
    s = open(tgt, errors="ignore").read()
    if "MIKO_STARTER_HORSE_V1" in s: return
    ex = ""
    if "UpdateHorseHealth(" in ch_h and "GetHorseMaxHealth(" in ch_h: ex += "\t\t\tch->UpdateHorseHealth(ch->GetHorseMaxHealth());\n"
    if "UpdateHorseStamina(" in ch_h and "GetHorseMaxStamina(" in ch_h: ex += "\t\t\tch->UpdateHorseStamina(ch->GetHorseMaxStamina());\n"
    inj = f'\n\t// MIKO_STARTER_HORSE_V1\n\tif (ch) {{\n\t\tif (ch->GetHorseLevel() < 21) {{ ch->SetHorseLevel(21);\n{ex}\t\t}}\n\t\tif (ch->GetSkillLevel(131) < 40) {{ ch->SetSkillLevel(131, 40); ch->SkillLevelPacket(); }}\n\t\tif (ch->CountSpecifyItem(50053) == 0) {{ ch->AutoGiveItem(50053, 1); }}\n\t}}\n'
    m1 = re.search(r"void\s+CInputLogin::EnterGame\s*\(", s)
    if not m1: return
    m2 = re.search(r"ch->Show\s*\([^;]+;\s*\n", s[m1.end():])
    if m2: open(tgt, "w").write(s[:m1.end()+m2.end()] + inj + s[m1.end()+m2.end():])
def patch_ox_and_summon():
    lua = "-- MIKO_OX_TR_V1\n" + "".join(f'add_ox_quiz(1, "{q}", {"true" if a else "false"})\n' for q, a in OX_TR)
    for r, _, fs in os.walk(PACK):
        for fn in fs:
            if "horse_summon" in fn.lower():
                p = os.path.join(r, fn); t = open(p, errors="ignore").read()
                t2 = re.sub(r"(skill_level\s*)==\s*10\b", r"\1>= 10", t)
                if t2 != t: open(p, "w").write(t2)
        if "oxquiz.lua" in fs or (os.path.basename(r) in ("english", "turkey") and "locale" in r):
            open(os.path.join(r, "oxquiz.lua"), "w", encoding="utf-8").write(lua)
if __name__ == "__main__":
    patch_plaza_npcs(); patch_horse_cpp(); patch_ox_and_summon()
