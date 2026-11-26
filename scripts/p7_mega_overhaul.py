import os, re, sys, json, struct, zipfile, subprocess, py_compile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def find_root():
    for c in [os.environ.get("ROOT", ""), os.getcwd(), os.path.dirname(REPO), "/tmp/m2build"]:
        if c and os.path.isdir(c) and (os.path.isdir(os.path.join(c, "clientsource")) or os.path.isdir(os.path.join(c, "android"))):
            return c
    return os.getcwd()

def find_files(root, name):
    out, target = [], name.lower()
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in (".git", "self-repo", "build", "__pycache__")]
        for fn in fns:
            if fn.lower() == target:
                out.append(os.path.join(dp, fn))
    return out

def safe_write_py(path, text):
    import re as _r
    orig = open(path, encoding="utf-8", errors="ignore").read() if os.path.exists(path) else ""
    t = _r.sub(r'^[ \t]+', lambda m: m.group(0).replace('\t', '    '), text, flags=_r.M)
    for cand in (t, text, _r.sub(r'^[ \t]+', lambda m: m.group(0).expandtabs(8), text, flags=_r.M)):
        try:
            compile(cand, path, "exec")
            open(path, "w", encoding="utf-8").write(cand)
            print("[P7] OK PY:", os.path.basename(path))
            return True
        except Exception as e:
            err = e
            if isinstance(e, SyntaxError) and not isinstance(e, (TabError, IndentationError)):
                open(path, "w", encoding="utf-8").write(cand)
                print("[P7] OK PY2:", os.path.basename(path))
                return True
    if orig:
        open(path, "w", encoding="utf-8").write(orig)
    print("[P7] ROLLBACK PY:", os.path.basename(path), err)
    return False


def png_to_dds(png_bytes, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    try:
        from PIL import Image
        import io
        im = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
        w, h = im.size
        r, g, b, a = im.split()
        raw = Image.merge("RGBA", (b, g, r, a)).tobytes()
        hdr = struct.pack(
            "<4s7I11I8I5I",
            b"DDS ", 124, 0x100F, h, w, w * 4, 0, 1,
            *([0] * 11),
            32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000,
            0x1000, 0, 0, 0, 0
        )
        open(out_path, "wb").write(hdr + raw)
        return True
    except Exception:
        tmp = out_path + ".tmp.png"
        open(tmp, "wb").write(png_bytes)
        try:
            subprocess.run(["convert", tmp, out_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            return False
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)

HUD_PATCH = r'''
# --- P7_MEGA_HUD_OVERHAUL ---
_M2_HUD_INST = None
_M2_HUD_CFG = "hud_layout.cfg"

def _m2_fit_icon(icon, slot):
    try:
        if not icon or not slot:
            return
        iw, ih = icon.GetWidth(), icon.GetHeight()
        sw, sh = slot.GetWidth(), slot.GetHeight()
        if iw <= 0 or ih <= 0 or sw <= 4 or sh <= 4:
            return
        pad = max(6, int(min(sw, sh) * 0.14))
        aw, ah = max(8, sw - pad), max(8, sh - pad)
        sc = min(float(aw) / float(iw), float(ah) / float(ih))
        if hasattr(icon, "SetScale"):
            icon.SetScale(sc, sc)
            dw, dh = int(iw * sc), int(ih * sc)
        else:
            dw, dh = iw, ih
        icon.SetPosition((sw - dw) // 2, (sh - dh) // 2)
        if hasattr(icon, "AddFlag"):
            icon.AddFlag("not_pick")
    except Exception:
        pass

def _m2_apply_hud_patch():
    import ui, player, mouseModule, os, json
    try:
        import chat
    except Exception:
        chat = None
    cls = globals().get("MobileHud")
    if not cls or getattr(cls, "_p7_done", False):
        return
    cls._p7_done = True
    _orig_init = cls.__init__
    _orig_upd = getattr(cls, "OnUpdate", None)
    _orig_icon = getattr(cls, "_MobileHud__SlotIcon", None)

    def _p7_init(self, *a, **k):
        global _M2_HUD_INST
        _orig_init(self, *a, **k)
        _M2_HUD_INST = self
        self._m2AtkHeld = False
        self._m2AtkBtn = None
        self._m2Edit = False
        self._m2DefPos = {}
        self._m2EditBar = []
        self._m2BindControls()
        self._m2LoadLayout()

    def _p7_slot_icon(self, *a, **k):
        res = _orig_icon(self, *a, **k) if _orig_icon else None
        try:
            slot = a[0] if len(a) > 0 else None
            if res and slot:
                _m2_fit_icon(res, slot)
            for v in self.__dict__.values():
                if isinstance(v, (list, tuple)):
                    for it in v:
                        if hasattr(it, "icon") and it.icon:
                            _m2_fit_icon(it.icon, it)
        except Exception:
            pass
        return res

    def _m2BindControls(self):
        # 1) Saldiri butonu: basili tutunca kesintisiz saldiri
        for name, obj in list(self.__dict__.items()):
            if not hasattr(obj, "GetWidth"):
                continue
            nl = name.lower()
            if any(k in nl for k in ("atk", "attack", "saldir")):
                self._m2AtkBtn = obj
                orig_down = getattr(obj, "OnMouseLeftButtonDown", None)
                orig_up = getattr(obj, "OnMouseLeftButtonUp", None)
                def _atk_down(s_btn=obj, od=orig_down, hud=self):
                    if hud._m2Edit:
                        return od() if od else None
                    hud._m2AtkHeld = True
                    try:
                        player.SetAttackKeyState(True)
                    except Exception:
                        pass
                    return od() if od else None
                def _atk_up(s_btn=obj, ou=orig_up, hud=self):
                    hud._m2AtkHeld = False
                    try:
                        player.SetAttackKeyState(False)
                    except Exception:
                        pass
                    return ou() if ou else None
                obj.OnMouseLeftButtonDown = _atk_down
                obj.OnMouseLeftButtonUp = _atk_up
                break

        # 2) Bos slotlara skill/esya atama + tam oturtma
        slot_lists = []
        for name, obj in list(self.__dict__.items()):
            if isinstance(obj, (list, tuple)) and obj and any(k in name.lower() for k in ("slot", "quick", "skill")):
                slot_lists.append(obj)
        for sl in slot_lists:
            for idx, sb in enumerate(sl):
                if not hasattr(sb, "SetEvent") and not hasattr(sb, "OnMouseLeftButtonUp"):
                    continue
                if hasattr(sb, "Enable"):
                    try: sb.Enable()
                    except Exception: pass
                orig_up = getattr(sb, "OnMouseLeftButtonUp", None)
                def _slot_up(i=idx, btn=sb, ou=orig_up, hud=self):
                    if hud._m2Edit:
                        return ou() if ou else None
                    try:
                        if mouseModule.mouseController.isAttached():
                            at = mouseModule.mouseController.GetAttachedType()
                            sn = mouseModule.mouseController.GetAttachedSlotNumber()
                            if at == player.SLOT_TYPE_QUICK_SLOT:
                                player.RequestMoveGlobalQuickSlotToLocalQuickSlot(sn, i)
                            else:
                                player.RequestAddLocalQuickSlot(i, at, sn)
                            mouseModule.mouseController.DeattachObject()
                            for rname in ("Refresh", "RefreshSlots", "_MobileHud__Refresh", "_MobileHud__RefreshSlots"):
                                fn = getattr(hud, rname, None)
                                if callable(fn):
                                    fn()
                                    break
                            return
                    except Exception:
                        pass
                    return ou() if ou else None
                sb.OnMouseLeftButtonUp = _slot_up
                if hasattr(sb, "icon") and sb.icon:
                    _m2_fit_icon(sb.icon, sb)

        # 3) HUD Yerlesim Duzenle butonu
        try:
            eb = ui.Button()
            eb.SetParent(self)
            eb.SetPosition(max(8, self.GetWidth() - 108), 8)
            eb.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
            eb.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
            eb.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
            eb.SetText("HUD Duzenle")
            eb.SetEvent(ui.__mem_func__(self.ToggleHudEdit))
            eb.Show()
            self._m2EditToggleBtn = eb
        except Exception:
            pass

    def _m2Widgets(self):
        ws = {}
        skip = {"_m2EditToggleBtn", "_m2SaveBtn", "_m2ResetBtn"}
        for name, obj in list(self.__dict__.items()):
            if name in skip:
                continue
            if hasattr(obj, "GetLocalPosition") and hasattr(obj, "SetPosition") and hasattr(obj, "AddFlag"):
                ws[name] = obj
            elif isinstance(obj, (list, tuple)):
                for i, it in enumerate(obj):
                    if hasattr(it, "GetLocalPosition") and hasattr(it, "SetPosition") and hasattr(it, "AddFlag"):
                        ws["%s_%d" % (name, i)] = it
        return ws

    def ToggleHudEdit(self):
        self._m2Edit = not getattr(self, "_m2Edit", False)
        ws = self._m2Widgets()
        if self._m2Edit:
            for k, w in ws.items():
                if k not in self._m2DefPos:
                    try: self._m2DefPos[k] = list(w.GetLocalPosition())
                    except Exception: pass
                try: w.AddFlag("movable")
                except Exception: pass
            self._m2ShowEditBar(True)
            if chat:
                chat.AppendChat(chat.CHAT_TYPE_INFO, "[HUD] Duzenleme acik: butonlari surukleyip Kaydet'e basin.")
        else:
            for w in ws.values():
                try: w.RemoveFlag("movable")
                except Exception: pass
            self._m2ShowEditBar(False)

    def _m2ShowEditBar(self, show):
        if show and not self._m2EditBar:
            try:
                cx = max(20, self.GetWidth() // 2 - 70)
                for lbl, dx, fn in (("Kaydet", 0, self._m2SaveLayout), ("Sifirla", 74, self._m2ResetLayout)):
                    b = ui.Button()
                    b.SetParent(self)
                    b.SetPosition(cx + dx, 10)
                    b.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
                    b.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
                    b.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
                    b.SetText(lbl)
                    b.SetEvent(ui.__mem_func__(fn))
                    b.Show()
                    self._m2EditBar.append(b)
            except Exception:
                pass
        for b in self._m2EditBar:
            try: b.Show() if show else b.Hide()
            except Exception: pass

    def _m2SaveLayout(self):
        data = {}
        for k, w in self._m2Widgets().items():
            try: data[k] = list(w.GetLocalPosition())
            except Exception: pass
        try:
            open(_M2_HUD_CFG, "w").write(json.dumps(data))
            if chat:
                chat.AppendChat(chat.CHAT_TYPE_INFO, "[HUD] Yerlesim kaydedildi.")
        except Exception:
            pass
        if self._m2Edit:
            self.ToggleHudEdit()

    def _m2ResetLayout(self):
        try:
            if os.path.exists(_M2_HUD_CFG):
                os.remove(_M2_HUD_CFG)
        except Exception:
            pass
        ws = self._m2Widgets()
        for k, pos in self._m2DefPos.items():
            if k in ws:
                try: ws[k].SetPosition(pos[0], pos[1])
                except Exception: pass
        if chat:
            chat.AppendChat(chat.CHAT_TYPE_INFO, "[HUD] Varsayilan yerlesime sifirlandi.")
        if self._m2Edit:
            self.ToggleHudEdit()

    def _m2LoadLayout(self):
        try:
            if not os.path.exists(_M2_HUD_CFG):
                return
            data = json.loads(open(_M2_HUD_CFG).read())
            ws = self._m2Widgets()
            for k, pos in data.items():
                if k in ws and len(pos) == 2:
                    if k not in self._m2DefPos:
                        self._m2DefPos[k] = list(ws[k].GetLocalPosition())
                    ws[k].SetPosition(int(pos[0]), int(pos[1]))
        except Exception:
            pass

    def _p7_upd(self):
        if _orig_upd:
            _orig_upd(self)
        if getattr(self, "_m2AtkHeld", False):
            try:
                b = getattr(self, "_m2AtkBtn", None)
                if b and hasattr(b, "IsDown") and not b.IsDown():
                    self._m2AtkHeld = False
                    player.SetAttackKeyState(False)
                else:
                    player.SetAttackKeyState(True)
            except Exception:
                pass

    cls.__init__ = _p7_init
    cls.OnUpdate = _p7_upd
    if _orig_icon:
        cls._MobileHud__SlotIcon = _p7_slot_icon
    cls._m2BindControls = _m2BindControls
    cls._m2Widgets = _m2Widgets
    cls.ToggleHudEdit = ToggleHudEdit
    cls._m2ShowEditBar = _m2ShowEditBar
    cls._m2SaveLayout = _m2SaveLayout
    cls._m2ResetLayout = _m2ResetLayout
    cls._m2LoadLayout = _m2LoadLayout

_m2_apply_hud_patch()
'''

INV_PATCH = r'''
# --- P7_SINGLE_TAP_INV ---
def _m2_patch_inv():
    import mouseModule, player
    cls = globals().get("InventoryWindow")
    if not cls or getattr(cls, "_p7_tap", False):
        return
    cls._p7_tap = True
    _orig_sel = getattr(cls, "SelectItemSlot", None)
    _orig_use = getattr(cls, "UseItemSlot", None)
    if not _orig_sel:
        return
    def _p7_sel(self, itemSlotIndex):
        try:
            if mouseModule.mouseController.isAttached():
                if mouseModule.mouseController.GetAttachedType() == player.SLOT_TYPE_INVENTORY and mouseModule.mouseController.GetAttachedSlotNumber() == itemSlotIndex:
                    mouseModule.mouseController.DeattachObject()
                    if _orig_use:
                        return _orig_use(self, itemSlotIndex)
        except Exception:
            pass
        return _orig_sel(self, itemSlotIndex)
    cls.SelectItemSlot = _p7_sel
_m2_patch_inv()
'''

OPT_PATCH = r'''
# --- P7_OPT_HUD_EDIT ---
def _m2_patch_opt():
    cls = None
    for v in list(globals().values()):
        if isinstance(v, type) and hasattr(v, "OnMikoHud"):
            cls = v
            break
    if not cls or getattr(cls, "_p7_opt", False):
        return
    cls._p7_opt = True
    _orig_hud = cls.OnMikoHud
    def _p7_miko_hud(self, *a, **k):
        try:
            import uimobilehud
            inst = getattr(uimobilehud, "_M2_HUD_INST", None)
            if inst and hasattr(inst, "ToggleHudEdit"):
                inst.ToggleHudEdit()
                return
        except Exception:
            pass
        return _orig_hud(self, *a, **k)
    cls.OnMikoHud = _p7_miko_hud
_m2_patch_opt()
'''

def patch_ui(root):
    for p in find_files(root, "uimobilehud.py"):
        s = open(p, encoding="utf-8", errors="ignore").read()
        if "P7_MEGA_HUD_OVERHAUL" not in s:
            s = re.sub(r'(def __SlotIcon[\s\S]{0,900}?)ui\.ImageBox\(\)', r'\1ui.ExpandedImageBox()', s)
            safe_write_py(p, s + "\n" + HUD_PATCH)
    for p in find_files(root, "uiinventory.py"):
        s = open(p, encoding="utf-8", errors="ignore").read()
        if "P7_SINGLE_TAP_INV" not in s:
            safe_write_py(p, s + "\n" + INV_PATCH)
    for p in find_files(root, "uidevoptions.py"):
        s = open(p, encoding="utf-8", errors="ignore").read()
        if "P7_OPT_HUD_EDIT" not in s:
            safe_write_py(p, s + "\n" + OPT_PATCH)
    for p in find_files(root, "GameView.java"):
        s = open(p, encoding="utf-8", errors="ignore").read()
        ns = re.sub(r'(LONG_PRESS\w*\s*=\s*)(?:4\d\d|5\d\d|6\d\d|7\d\d|8\d\d)', r'\g<1>260', s)
        if ns != s:
            open(p, "w", encoding="utf-8").write(ns)
            print("[P7] OK JAVA:", os.path.basename(p))

def find_ymir_dir(root):
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in (".git", "self-repo", "build")]
        if os.path.basename(dp).lower() == "ymir work":
            return dp
    return os.path.join(root, "android", "assets", "ymir work")

def patch_zips(root):
    ymir = find_ymir_dir(root)
    print("[P7] YMIR:", ymir)

    # 1) 120 Lvl Altin Aura
    az = os.path.join(REPO, "metin2_lvl120_altin_aura_3d_paket.zip")
    if os.path.isfile(az):
        z = zipfile.ZipFile(az)
        mse_text, reg_code, off = "", "", 55
        for n in z.namelist():
            if n.endswith(".mse"):
                mse_text = z.read(n).decode("utf-8", "ignore")
                for sub in ("effect/etc/levelup_120/lvl120_gold_aura.mse", "effect/lvl120_gold_aura/lvl120_gold_aura.mse"):
                    dst = os.path.join(ymir, sub)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    open(dst, "wb").write(z.read(n))
            elif "01_playersettingmodule" in n:
                reg_code = z.read(n).decode("utf-8", "ignore")
                m = re.search(r'EFFECT_AFFECT\s*\+\s*(\d+)', reg_code)
                if m:
                    off = int(m.group(1))
        tex_dirs = set(["effect/etc/levelup_120", "effect/lvl120_gold_aura"])
        for tp in re.findall(r'd:/ymir work/([^"\s]+?)/[^/"\s]+\.(?:dds|tga)', mse_text, re.I):
            tex_dirs.add(tp)
        for n in z.namelist():
            if n.lower().endswith(".png"):
                base = os.path.splitext(os.path.basename(n))[0] + ".dds"
                data = z.read(n)
                for td in tex_dirs:
                    png_to_dds(data, os.path.join(ymir, td, base))
        for p in find_files(root, "playersettingmodule.py"):
            s = open(p, encoding="utf-8", errors="ignore").read()
            if "P7_LVL120_AURA" not in s:
                snippet = f'\n# P7_LVL120_AURA\ntry:\n\tchrmgr.RegisterEffect(chrmgr.EFFECT_AFFECT + {off}, "", "d:/ymir work/effect/etc/levelup_120/lvl120_gold_aura.mse")\nexcept Exception:\n\tpass\n'
                safe_write_py(p, s + snippet)
        for p in find_files(root, "InstanceBaseEffect.cpp"):
            s = open(p, encoding="utf-8", errors="ignore").read()
            if "P7_LVL120_AURA" not in s and "EFFECT_AFFECT" in s and "__AttachEffect(" in s and "GetVirtualID(" in s:
                m = re.search(r'(void\s+CInstanceBase::UpdateTextTailLevel\s*\(\s*DWORD\s+(\w+)\s*\)\s*\{)', s)
                if m:
                    inc = "#include <set>\n" if "#include <set>" not in s else ""
                    inj = f'\n\t// P7_LVL120_AURA\n\tif ({m.group(2)} >= 120) {{ static std::set<DWORD> _a120; if (_a120.size() > 512) _a120.clear(); if (_a120.insert(GetVirtualID()).second) __AttachEffect(EFFECT_AFFECT + {off}); }}\n'
                    open(p, "w", encoding="utf-8").write(inc + s.replace(m.group(1), m.group(1) + inj, 1))
                    print("[P7] OK CPP AURA120 (off=%d)" % off)

    # 2) Mavi / Kirmizi / Sari Koy HD Doku + Atmosfer (.msenv)
    env_map = {"c1": "c1_remastered_hd.msenv", "a1": "a1_remastered_hd.msenv", "b1": "b1_remastered_hd.msenv"}
    for zn in ("metin2_mavi1_remastered_v2_paket.zip", "metin2_sari_kirmizi_koy_v2_final.zip"):
        zp = os.path.join(REPO, zn)
        if not os.path.isfile(zp):
            continue
        z = zipfile.ZipFile(zp)
        cnt = 0
        for n in z.namelist():
            nl = n.lower()
            if nl.endswith(".msenv"):
                dst = os.path.join(ymir, "environment", os.path.basename(n))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                open(dst, "wb").write(z.read(n))
                cnt += 1
            elif nl.endswith(".png") and "textures_png/" in nl:
                base = os.path.splitext(os.path.basename(n))[0] + ".dds"
                if png_to_dds(z.read(n), os.path.join(ymir, "zone", "remastered_hd", base)):
                    cnt += 1
        print(f"[P7] OK ZIP {zn}: {cnt} asset")

    for code, msenv in env_map.items():
        for dp, dns, fns in os.walk(root):
            if os.path.basename(dp).lower() == f"metin2_map_{code}":
                for fn in fns:
                    if fn.lower() == "setting.txt":
                        sp = os.path.join(dp, fn)
                        st = open(sp, encoding="utf-8", errors="ignore").read()
                        nst = re.sub(r'(?im)^Environment\s+.*$', f'Environment\t{msenv}', st)
                        if nst != st:
                            open(sp, "w", encoding="utf-8").write(nst)
                            print("[P7] OK ENV:", f"metin2_map_{code} -> {msenv}")

def main():
    root = find_root()
    print("[P7] ROOT:", root)
    patch_ui(root)
    patch_zips(root)

if __name__ == "__main__":
    main()
