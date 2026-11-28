#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, re, shutil, sqlite3, subprocess, sys, urllib.request, zipfile

REL_REPO = "zenfasulyesi55-afk/Metin2-Lab"
BUNDLE_URL = "https://github.com/%s/releases/download/saltanat-assets-v1/saltanat_kraliyet_bundle.zip" % REL_REPO
BUNDLE_LOCAL = "/tmp/saltanat_kraliyet_bundle.zip"

def _find_files(name):
    hits = []
    for base in ("client-src", "server-src", "/tmp/m2stage", "/tmp/m2serverpack", "."):
        if not os.path.isdir(base):
            continue
        for r, ds, fs in os.walk(base):
            ds[:] = [d for d in ds if d not in (".git", "build", ".gradle")]
            for f in fs:
                if f.lower() == name.lower():
                    p = os.path.abspath(os.path.join(r, f))
                    if p not in hits:
                        hits.append(p)
    return hits

def _balanced(code):
    return code.count("{") == code.count("}") and code.count("(") == code.count(")")

def _auth_header():
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        return "Bearer " + tok.strip()
    for cfg in (".git/config", "self-repo/.git/config"):
        if os.path.isfile(cfg):
            t = open(cfg, encoding="utf-8", errors="ignore").read()
            m = re.search(r"extraheader\s*=\s*AUTHORIZATION:\s*(.+)", t, re.I)
            if m:
                return m.group(1).strip()
    return None

def ensure_bundle():
    if os.path.isfile(BUNDLE_LOCAL) and zipfile.is_zipfile(BUNDLE_LOCAL):
        return BUNDLE_LOCAL
    print("[p10] Saltanat paketi indiriliyor...")
    try:
        urllib.request.urlretrieve(BUNDLE_URL, BUNDLE_LOCAL)
        if zipfile.is_zipfile(BUNDLE_LOCAL):
            return BUNDLE_LOCAL
    except Exception:
        pass
    subprocess.run(
        ["gh", "release", "download", "saltanat-assets-v1", "-R", REL_REPO,
         "-p", "saltanat_kraliyet_bundle.zip", "-D", "/tmp", "--clobber"],
        check=False
    )
    if os.path.isfile(BUNDLE_LOCAL) and zipfile.is_zipfile(BUNDLE_LOCAL):
        return BUNDLE_LOCAL
    ah = _auth_header()
    if ah:
        try:
            api = "https://api.github.com/repos/%s/releases/tags/saltanat-assets-v1" % REL_REPO
            req = urllib.request.Request(api, headers={"Authorization": ah, "User-Agent": "m2-p10"})
            rel = json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8"))
            for a in rel.get("assets", []):
                if a.get("name") == "saltanat_kraliyet_bundle.zip":
                    areq = urllib.request.Request(
                        a["url"],
                        headers={"Authorization": ah, "Accept": "application/octet-stream", "User-Agent": "m2-p10"}
                    )
                    with urllib.request.urlopen(areq, timeout=180) as r, open(BUNDLE_LOCAL, "wb") as fo:
                        shutil.copyfileobj(r, fo)
                    break
        except Exception as e:
            print("[p10] API indirme uyarisi:", e)
    return BUNDLE_LOCAL if os.path.isfile(BUNDLE_LOCAL) and zipfile.is_zipfile(BUNDLE_LOCAL) else None

def patch_joystick_java():
    for jp in _find_files("JoystickView.java"):
        src = open(jp, encoding="utf-8", errors="ignore").read()
        if "SALTANAT_DYN_JOY_V10" in src:
            continue
        orig = src
        src = re.sub(r"Color\.argb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)", "0x66121722", src, count=1)
        src = re.sub(r"new\s+Paint\s*\(\s*\)", "new Paint(Paint.ANTI_ALIAS_FLAG)", src)
        cx = next((n for n in ("centerX", "mCenterX", "baseX", "cx") if re.search(r"\b" + n + r"\b", src)), None)
        cy = next((n for n in ("centerY", "mCenterY", "baseY", "cy") if re.search(r"\b" + n + r"\b", src)), None)
        if cx and cy and "ACTION_DOWN" in src:
            dyn_down = (
                "/* SALTANAT_DYN_JOY_V10 */ setAlpha(1.0f); "
                "float _pad = Math.min(getWidth(), getHeight()) * 0.28f; "
                + cx + " = Math.max(_pad, Math.min(getWidth() - _pad, event.getX())); "
                + cy + " = Math.max(_pad, Math.min(getHeight() - _pad, event.getY()));"
            )
            src = re.sub(r"(case\s+MotionEvent\.ACTION_DOWN\s*:)", r"\1 " + dyn_down, src, count=1)
            src = re.sub(r"(case\s+MotionEvent\.ACTION_UP\s*:)", r"\1 setAlpha(0.32f);", src, count=1)
        elif "onTouchEvent" in src:
            src = src.replace("onTouchEvent(MotionEvent", "/* SALTANAT_DYN_JOY_V10 */ onTouchEvent(MotionEvent", 1)
            src = re.sub(r"(ACTION_DOWN[^;{]*[:{])", r"\1 setAlpha(1.0f);", src, count=1)
            src = re.sub(r"(ACTION_UP[^;{]*[:{])", r"\1 setAlpha(0.32f);", src, count=1)
        if _balanced(src) and src != orig:
            open(jp, "w", encoding="utf-8").write(src)
            print("[p10] JoystickView dinamik moda alindi:", jp)

def patch_mainactivity_android():
    for mp in _find_files("MainActivity.java"):
        src = open(mp, encoding="utf-8", errors="ignore").read()
        if "SALTANAT_ANDROID_UI_V10" in src:
            continue
        orig = src
        immersive = (
            " /* SALTANAT_ANDROID_UI_V10 */ try { "
            "getWindow().getDecorView().setBackgroundColor(0xFF0B0E14); "
            "getWindow().getDecorView().setSystemUiVisibility("
            "android.view.View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY | "
            "android.view.View.SYSTEM_UI_FLAG_FULLSCREEN | "
            "android.view.View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | "
            "android.view.View.SYSTEM_UI_FLAG_LAYOUT_STABLE | "
            "android.view.View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN | "
            "android.view.View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION); "
            "} catch (Throwable _e) {} "
        )
        src = re.sub(r"(super\.onCreate\s*\([^)]*\)\s*;)", r"\1" + immersive, src, count=1)
        src = src.replace("0xFF1A1A2E", "0xFF0E131D").replace("0xFF16213E", "0xFF141B29")
        src = src.replace("Color.DKGRAY", "0xFF141B29").replace("Color.BLACK", "0xFF0B0E14")
        if _balanced(src) and src != orig:
            open(mp, "w", encoding="utf-8").write(src)
            print("[p10] MainActivity modern Android UI uygulandi:", mp)

HUD_PY2 = '''# -*- coding: utf-8 -*-
import os, app, net, player, wndMgr, ui, grp, chat, item

_GFX_CFG = {"view": 1, "fog": 0, "shadow": 0, "effect": 1, "scale": 1.0}

def LoadGfxConfig():
    return dict(_GFX_CFG)

def SaveGfxConfig(c):
    if isinstance(c, dict):
        _GFX_CFG.update(c)

def ApplyGfxLive(c=None):
    if isinstance(c, dict):
        _GFX_CFG.update(c)

def LoadDisplayConf():
    return dict(_GFX_CFG)

def SaveDisplayConf(c):
    SaveGfxConfig(c)

class _GlassBtn(ui.Window):
    def __init__(self, parent, x, y, w, h, label, bg=0xAA101622, border=0xFFD4AF37, cb=None):
        ui.Window.__init__(self)
        if parent is not None:
            self.SetParent(parent)
        self.SetPosition(x, y)
        self.SetSize(w, h)
        self._cb = cb
        self._bg = bg
        self._fill = ui.Bar()
        self._fill.SetParent(self)
        self._fill.AddFlag("not_pick")
        self._fill.SetPosition(0, 0)
        self._fill.SetSize(w, h)
        self._fill.SetColor(bg)
        self._fill.Show()
        self._border = ui.Box()
        self._border.SetParent(self)
        self._border.AddFlag("not_pick")
        self._border.SetPosition(0, 0)
        self._border.SetSize(w, h)
        self._border.SetColor(border)
        self._border.Show()
        self._txt = ui.TextLine()
        self._txt.SetParent(self)
        self._txt.AddFlag("not_pick")
        self._txt.SetPosition(w // 2, h // 2)
        self._txt.SetHorizontalAlignCenter()
        self._txt.SetVerticalAlignCenter()
        self._txt.SetPackedFontColor(0xFFF5E6C4)
        self._txt.SetText(label)
        self._txt.Show()
        self.Show()

    def OnMouseLeftButtonDown(self):
        self._fill.SetColor(0xCC2A3548)
        if self._cb:
            try:
                self._cb()
            except Exception:
                pass
        return True

    def OnMouseLeftButtonUp(self):
        self._fill.SetColor(self._bg)
        return True

class SaltanatMobileHUD(ui.Window):
    def __init__(self, *args, **kwargs):
        ui.Window.__init__(self)
        self.interface = args[0] if args else kwargs.get("interface", None)
        self.menuOpen = False
        self._widgets = []
        self.menuBtns = []
        self._built = False
        self.SetSize(0, 0)
        self.SetPosition(0, 0)
        self.Build()

    def BindInterface(self, interface):
        self.interface = interface

    def SetInterface(self, interface):
        self.interface = interface

    def Build(self):
        if self._built:
            return
        self._built = True
        sw = wndMgr.GetScreenWidth()
        sh = wndMgr.GetScreenHeight()

        self.menuToggle = _GlassBtn(None, sw - 96, 12, 84, 34, "MENU", 0xCC121824, 0xFFD4AF37, self.ToggleMenu)
        self._widgets.append(self.menuToggle)

        self.drawer = ui.Window()
        self.drawer.SetPosition(sw - 134, 52)
        self.drawer.SetSize(122, 248)
        self._drawerBg = ui.Bar()
        self._drawerBg.SetParent(self.drawer)
        self._drawerBg.AddFlag("not_pick")
        self._drawerBg.SetPosition(0, 0)
        self._drawerBg.SetSize(122, 248)
        self._drawerBg.SetColor(0xDD0D121C)
        self._drawerBg.Show()
        self.drawer.Hide()

        items = [
            ("Envanter", self._open_inv),
            ("Karakter", self._open_char),
            ("Beceriler", self._open_skill),
            ("Sohbet", self._open_chat),
            ("Binek Bin", self._mount),
            ("Pet Cagir", self._pet),
            ("Sehir Don", self._warp_town),
        ]
        for idx, (lbl, fn) in enumerate(items):
            b = _GlassBtn(self.drawer, 6, 6 + idx * 34, 110, 30, lbl, 0xBB182235, 0xAA9E8242, fn)
            self.menuBtns.append(b)

        ax, ay = sw - 92, sh - 92
        self.atkBtn = _GlassBtn(None, ax, ay, 76, 76, "SALDIRI", 0xCC7A1C1C, 0xFFE6C15A, self._attack_tap)
        self.pickBtn = _GlassBtn(None, sw - 166, sh - 46, 66, 32, "TOPLA", 0xBB162820, 0xFF66BB6A, self._pickup)
        self.mntBtn = _GlassBtn(None, sw - 166, sh - 84, 66, 32, "BINEK", 0xBB1C2236, 0xFFD4AF37, self._mount)
        self._widgets.extend([self.atkBtn, self.pickBtn, self.mntBtn])

        coords = [
            (sw - 236, sh - 52), (sw - 236, sh - 102), (sw - 186, sh - 138), (sw - 132, sh - 148),
            (sw - 78, sh - 148), (sw - 288, sh - 52), (sw - 288, sh - 102), (sw - 242, sh - 150)
        ]
        labels = ["1", "2", "3", "4", "F1", "F2", "F3", "F4"]
        for i in range(8):
            x, y = coords[i]
            btn = _GlassBtn(None, x, y, 44, 44, labels[i], 0xBB101828, 0xFFC8A24A, lambda s=i: self._use_slot(s))
            self._widgets.append(btn)

    def ToggleMenu(self):
        self.menuOpen = not self.menuOpen
        if self.menuOpen:
            self.drawer.Show()
            self.drawer.SetTop()
        else:
            self.drawer.Hide()

    def _use_slot(self, idx):
        try:
            player.RequestUseLocalQuickSlot(idx)
        except Exception:
            pass

    def _attack_tap(self):
        try:
            player.SetAttackKeyState(True)
            player.SetAttackKeyState(False)
        except Exception:
            pass

    def _pickup(self):
        try:
            player.PickCloseItem()
        except Exception:
            pass

    def _mount(self):
        try:
            net.SendChatPacket("/user_horse_ride")
        except Exception:
            pass
        try:
            net.SendChatPacket("/mount_test 20240")
        except Exception:
            pass

    def _pet(self):
        try:
            for slot in range(90):
                v = player.GetItemIndex(slot)
                if v in (53001, 53002, 53003, 53005, 53006, 53007, 53008, 53009, 53010):
                    net.SendItemUsePacket(slot)
                    return
            net.SendChatPacket("/m 34001")
        except Exception:
            pass

    def _warp_town(self):
        if self.menuOpen:
            self.ToggleMenu()
        try:
            net.SendChatPacket("/go c")
        except Exception:
            pass

    def _open_inv(self):
        if self.menuOpen:
            self.ToggleMenu()
        try:
            if self.interface:
                self.interface.ToggleInventoryWindow()
        except Exception:
            pass

    def _open_char(self):
        if self.menuOpen:
            self.ToggleMenu()
        try:
            if self.interface:
                self.interface.ToggleCharacterWindow("STATUS")
        except Exception:
            pass

    def _open_skill(self):
        if self.menuOpen:
            self.ToggleMenu()
        try:
            if self.interface:
                self.interface.ToggleCharacterWindow("SKILL")
        except Exception:
            pass

    def _open_chat(self):
        if self.menuOpen:
            self.ToggleMenu()
        try:
            if self.interface and hasattr(self.interface, "ToggleChat"):
                self.interface.ToggleChat()
        except Exception:
            pass

    def Show(self):
        ui.Window.Show(self)
        for w in self._widgets:
            w.Show()

    def Hide(self):
        ui.Window.Hide(self)
        for w in self._widgets:
            w.Hide()
        self.drawer.Hide()
        self.menuOpen = False

    def Open(self):
        self.Show()

    def Close(self):
        self.Hide()

    def OnUpdate(self):
        pass

    def Refresh(self):
        pass

    def __getattr__(self, name):
        return lambda *a, **kw: None
'''

INV_SINGLE_TAP_PY2 = '''
# === SALTANAT_SINGLE_TAP_INV_V10 ===
try:
    import time as _st_time, ui as _st_ui, net as _st_net, player as _st_player, wndMgr as _st_wnd
    class _AndroidTapBtn(_st_ui.Window):
        def __init__(self, parent, x, y, w, h, lbl, col, fn):
            _st_ui.Window.__init__(self)
            self.SetParent(parent)
            self.SetPosition(x, y)
            self.SetSize(w, h)
            self._fn = fn
            bg = _st_ui.Bar()
            bg.SetParent(self); bg.AddFlag("not_pick"); bg.SetPosition(0, 0); bg.SetSize(w, h); bg.SetColor(col); bg.Show()
            t = _st_ui.TextLine()
            t.SetParent(self); t.AddFlag("not_pick"); t.SetPosition(w // 2, h // 2)
            t.SetHorizontalAlignCenter(); t.SetVerticalAlignCenter()
            t.SetPackedFontColor(0xFFF5E6C4); t.SetText(lbl); t.Show()
            self._parts = (bg, t)
            self.Show()
        def OnMouseLeftButtonDown(self):
            try:
                self._fn()
            except Exception:
                pass
            return True

    class _AndroidItemBar(_st_ui.Window):
        def __init__(self):
            _st_ui.Window.__init__(self)
            sw, sh = _st_wnd.GetScreenWidth(), _st_wnd.GetScreenHeight()
            self.SetSize(316, 48)
            self.SetPosition((sw - 316) // 2, sh - 62)
            bg = _st_ui.Bar()
            bg.SetParent(self); bg.AddFlag("not_pick"); bg.SetPosition(0, 0); bg.SetSize(316, 48); bg.SetColor(0xEE0E1420); bg.Show()
            self._bg = bg
            self.slot = -1
            specs = [
                ("KULLAN/GIY", 0xCC1E5631, 6, 96, self._use),
                ("SLOTA KOY", 0xCC1B3B6F, 108, 92, self._qslot),
                ("SAT/AT", 0xCC6E2626, 206, 66, self._drop),
                ("X", 0xCC333A48, 278, 32, self.Hide),
            ]
            self._btns = [_AndroidTapBtn(self, x, 6, w, 36, lbl, col, fn) for (lbl, col, x, w, fn) in specs]
            self.Hide()
        def OpenFor(self, slot):
            self.slot = slot
            self.Show()
            self.SetTop()
        def _use(self):
            try:
                _st_net.SendItemUsePacket(self.slot)
            except Exception:
                pass
            self.Hide()
        def _qslot(self):
            try:
                for i in range(8):
                    t, p = _st_player.GetLocalQuickSlot(i)
                    if t == 0:
                        _st_player.RequestAddLocalQuickSlot(i, _st_player.SLOT_TYPE_INVENTORY, self.slot)
                        break
            except Exception:
                pass
            self.Hide()
        def _drop(self):
            try:
                _st_net.SendItemDropPacketNew(self.slot, 1)
            except Exception:
                try:
                    _st_net.SendItemDropPacket(self.slot)
                except Exception:
                    pass
            self.Hide()

    _ST_BAR = None
    _ST_LAST = [-1, 0.0]
    if "InventoryWindow" in globals() and hasattr(InventoryWindow, "SelectItemSlot"):
        _orig_sel = InventoryWindow.SelectItemSlot
        def _android_sel(self, itemSlotIndex):
            global _ST_BAR
            try:
                now = _st_time.time()
                slot = self._InventoryWindow__InventoryLocalSlotPosToGlobalSlotPos(itemSlotIndex) if hasattr(self, "_InventoryWindow__InventoryLocalSlotPosToGlobalSlotPos") else itemSlotIndex
                if _ST_LAST[0] == slot and (now - _ST_LAST[1]) < 0.45:
                    _ST_LAST[0] = -1
                    if _ST_BAR:
                        _ST_BAR.Hide()
                    _st_net.SendItemUsePacket(slot)
                    return
                _ST_LAST[0] = slot
                _ST_LAST[1] = now
                if _ST_BAR is None:
                    _ST_BAR = _AndroidItemBar()
                _ST_BAR.OpenFor(slot)
            except Exception:
                pass
            return _orig_sel(self, itemSlotIndex)
        InventoryWindow.SelectItemSlot = _android_sel
except Exception:
    pass
'''

SHOP_SINGLE_TAP_PY2 = '''
# === SALTANAT_SINGLE_TAP_SHOP_V10 ===
try:
    import time as _sh_time, ui as _sh_ui, net as _sh_net, wndMgr as _sh_wnd
    class _ShopTapBtn(_sh_ui.Window):
        def __init__(self, parent, x, y, w, h, lbl, col, fn):
            _sh_ui.Window.__init__(self)
            self.SetParent(parent)
            self.SetPosition(x, y)
            self.SetSize(w, h)
            self._fn = fn
            bg = _sh_ui.Bar()
            bg.SetParent(self); bg.AddFlag("not_pick"); bg.SetPosition(0, 0); bg.SetSize(w, h); bg.SetColor(col); bg.Show()
            t = _sh_ui.TextLine()
            t.SetParent(self); t.AddFlag("not_pick"); t.SetPosition(w // 2, h // 2)
            t.SetHorizontalAlignCenter(); t.SetVerticalAlignCenter()
            t.SetPackedFontColor(0xFFF5E6C4); t.SetText(lbl); t.Show()
            self._parts = (bg, t)
            self.Show()
        def OnMouseLeftButtonDown(self):
            try:
                self._fn()
            except Exception:
                pass
            return True

    class _AndroidShopBar(_sh_ui.Window):
        def __init__(self):
            _sh_ui.Window.__init__(self)
            sw, sh = _sh_wnd.GetScreenWidth(), _sh_wnd.GetScreenHeight()
            self.SetSize(224, 48)
            self.SetPosition((sw - 224) // 2, sh - 62)
            bg = _sh_ui.Bar()
            bg.SetParent(self); bg.AddFlag("not_pick"); bg.SetPosition(0, 0); bg.SetSize(224, 48); bg.SetColor(0xEE0E1420); bg.Show()
            self._bg = bg
            self.slot = -1
            self._items = [
                _ShopTapBtn(self, 6, 6, 136, 36, "SATIN AL", 0xCC1E5631, self._buy),
                _ShopTapBtn(self, 148, 6, 70, 36, "IPTAL", 0xCC4A2020, self.Hide),
            ]
            self.Hide()
        def OpenFor(self, slot):
            self.slot = slot
            self.Show()
            self.SetTop()
        def _buy(self):
            try:
                _sh_net.SendShopBuyPacket(self.slot)
            except Exception:
                pass
            self.Hide()

    _SH_BAR = None
    _SH_LAST = [-1, 0.0]
    if "ShopDialog" in globals() and hasattr(ShopDialog, "SelectItemSlot"):
        _orig_shop_sel = ShopDialog.SelectItemSlot
        def _android_shop_sel(self, selectedSlotPos):
            global _SH_BAR
            try:
                now = _sh_time.time()
                if _SH_LAST[0] == selectedSlotPos and (now - _SH_LAST[1]) < 0.45:
                    _SH_LAST[0] = -1
                    if _SH_BAR:
                        _SH_BAR.Hide()
                    _sh_net.SendShopBuyPacket(selectedSlotPos)
                    return
                _SH_LAST[0] = selectedSlotPos
                _SH_LAST[1] = now
                if _SH_BAR is None:
                    _SH_BAR = _AndroidShopBar()
                _SH_BAR.OpenFor(selectedSlotPos)
            except Exception:
                pass
            return _orig_shop_sel(self, selectedSlotPos)
        ShopDialog.SelectItemSlot = _android_shop_sel
except Exception:
    pass
'''

def patch_python_ui():
    known_defs = {"LoadGfxConfig", "SaveGfxConfig", "ApplyGfxLive", "LoadDisplayConf", "SaveDisplayConf"}
    for hp in _find_files("uimobilehud.py"):
        orig = open(hp, encoding="utf-8", errors="ignore").read()
        classes = re.findall(r"^class\s+(\w+)", orig, re.M)
        funcs = re.findall(r"^def\s+(\w+)", orig, re.M)
        out = HUD_PY2 + "\n"
        for c in sorted(set(classes)):
            if c != "SaltanatMobileHUD" and not c.startswith("_"):
                out += "%s = SaltanatMobileHUD\n" % c
        if "MobileHUD" not in classes:
            out += "MobileHUD = SaltanatMobileHUD\n"
        for fn in sorted(set(funcs)):
            if fn not in known_defs and not fn.startswith("_"):
                out += "def %s(*a, **kw):\n    return None\n" % fn
        open(hp, "w", encoding="utf-8").write(out)
        print("[p10] uimobilehud yenilendi:", hp)

    for ip in _find_files("uiinventory.py"):
        t = open(ip, encoding="utf-8", errors="ignore").read()
        if "SALTANAT_SINGLE_TAP_INV_V10" not in t:
            open(ip, "w", encoding="utf-8").write(t + "\n" + INV_SINGLE_TAP_PY2)
            print("[p10] uiinventory tek dokunus eklendi:", ip)

    for sp in _find_files("uishop.py"):
        t = open(sp, encoding="utf-8", errors="ignore").read()
        if "SALTANAT_SINGLE_TAP_SHOP_V10" not in t:
            open(sp, "w", encoding="utf-8").write(t + "\n" + SHOP_SINGLE_TAP_PY2)
            print("[p10] uishop tek dokunus eklendi:", sp)

def patch_level300_everywhere():
    for base in ("server-src",):
        if not os.path.isdir(base):
            continue
        for r, ds, fs in os.walk(base):
            ds[:] = [d for d in ds if d != ".git"]
            for f in fs:
                if f.endswith((".h", ".hpp", ".cpp")):
                    p = os.path.join(r, f)
                    t = open(p, encoding="utf-8", errors="ignore").read()
                    nt = re.sub(r"(PLAYER_MAX_LEVEL_CONST\s*=\s*)\d+", r"\g<1>300", t)
                    nt = re.sub(r"(gPlayerMaxLevel\s*=\s*)\d+", r"\g<1>300", nt)
                    if nt != t:
                        open(p, "w", encoding="utf-8").write(nt)
                        print("[p10] C++ MAX_LEVEL=300:", p)
    for cp in _find_files("CONFIG"):
        t = open(cp, encoding="utf-8", errors="ignore").read()
        if re.search(r"(?im)^MAX_LEVEL\s*:", t):
            nt = re.sub(r"(?im)^MAX_LEVEL\s*:\s*\d+", "MAX_LEVEL: 300", t)
        else:
            nt = t.rstrip() + "\nMAX_LEVEL: 300\n"
        if nt != t:
            open(cp, "w", encoding="utf-8").write(nt)
            print("[p10] CONFIG MAX_LEVEL=300:", cp)

def patch_sqlite_saltanat():
    for dbp in _find_files("player.sqlite"):
        try:
            con = sqlite3.connect(dbp)
            cur = con.cursor()
            tbls = {r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if "shop" in tbls and "shop_item" in tbls:
                cur.execute("INSERT OR IGNORE INTO shop (vnum, name, npc_vnum) VALUES (900, 'Saltanat Market', 20400)")
                saltanat_items = [
                    (900, 19, 1), (900, 149, 1), (900, 299, 1), (900, 11299, 1),
                    (900, 71124, 1), (900, 53001, 1), (900, 27992, 5), (900, 27993, 5), (900, 27994, 5)
                ]
                for row in saltanat_items:
                    cur.execute("INSERT OR IGNORE INTO shop_item (shop_vnum, item_vnum, count) VALUES (?,?,?)", row)
            if "refine_proto" in tbls:
                cur.execute("UPDATE refine_proto SET prob = 100 WHERE prob < 100")
            con.commit()
            con.close()
            print("[p10] SQLite Saltanat uygulandi:", dbp)
        except Exception as e:
            print("[p10] SQLite uyari:", e)

def apply_saltanat_bundle():
    bp = ensure_bundle()
    if not bp:
        print("[p10] UYARI: Saltanat bundle bulunamadi")
        return
    zf = zipfile.ZipFile(bp)
    for base in ("/tmp/m2serverpack/server", "/tmp/m2serverpack"):
        if not os.path.isdir(base):
            continue
        for r, _, fs in os.walk(base):
            for f in fs:
                fl = f.lower()
                key = "server/data/" + fl
                if fl in ("mob_drop_item.txt", "special_item_group.txt") and key in zf.namelist():
                    open(os.path.join(r, f), "wb").write(zf.read(key))
                    print("[p10] Saltanat drop uygulandi:", os.path.join(r, f))
    stage = "/tmp/m2stage"
    if os.path.isdir(stage):
        for mp in ("metin2_map_a1", "metin2_map_b1", "metin2_map_c1"):
            old_m = os.path.join(stage, mp)
            if os.path.isdir(old_m):
                shutil.rmtree(old_m, ignore_errors=True)
        extracted = 0
        for info in zf.infolist():
            fn = info.filename
            if info.is_dir():
                continue
            if fn.startswith("client/maps/"):
                rel = fn[len("client/maps/"):]
            elif fn.startswith("client/icon/"):
                rel = fn[len("client/"):]
            elif fn.startswith("client/a_maviruhkraliyet"):
                rel = fn[len("client/"):]
            else:
                continue
            tp = os.path.join(stage, rel)
            os.makedirs(os.path.dirname(tp), exist_ok=True)
            open(tp, "wb").write(zf.read(info))
            extracted += 1
        for mp in ("metin2_map_a1", "metin2_map_b1", "metin2_map_c1"):
            st = os.path.join(stage, mp, "setting.txt")
            if os.path.isfile(st):
                txt = open(st, encoding="utf-8", errors="ignore").read()
                txt = re.sub(r"(?im)^Environment\s+.*$", "Environment\ta1.msenv", txt)
                open(st, "w", encoding="utf-8").write(txt)
        print("[p10] Temiz Saltanat harita/varlik aktarildi:", extracted)

def run(stage_only=False):
    if not stage_only:
        patch_level300_everywhere()
        patch_joystick_java()
        patch_mainactivity_android()
    patch_python_ui()
    patch_level300_everywhere()
    patch_sqlite_saltanat()
    apply_saltanat_bundle()

if __name__ == "__main__":
    run("--stage-only" in sys.argv)
