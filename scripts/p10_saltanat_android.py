#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, re, shutil, sqlite3, subprocess, sys, urllib.request, zipfile

REL_REPO = "zenfasulyesi55-afk/Metin2-Lab"
BUNDLE_URL = "https://github.com/%s/releases/download/saltanat-assets-v1/saltanat_kraliyet_bundle.zip" % REL_REPO
BUNDLE_LOCAL = "/tmp/saltanat_kraliyet_bundle.zip"
HUD_MARK = "# === SALTANAT_HUD_V10_SAFE ==="
INV_MARK = "# === SALTANAT_SINGLE_TAP_INV_V10 ==="
SHOP_MARK = "# === SALTANAT_SINGLE_TAP_SHOP_V10 ==="
LOGIN_MARK = "# === SALTANAT_ANDROID_LOGIN_V10 ==="

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
        if "SALTANAT_ANDROID_UI_V10_B" in src:
            continue
        orig = src
        immersive = (
            " /* SALTANAT_ANDROID_UI_V10_B */ try { "
            "getWindow().getDecorView().setBackgroundColor(0xFF0A0D14); "
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
        src = src.replace("0xFF1A1A2E", "0xFF0C1018").replace("0xFF16213E", "0xFF121926")
        src = src.replace("Color.DKGRAY", "0xFF121926").replace("Color.BLACK", "0xFF0A0D14")
        if _balanced(src) and src != orig:
            open(mp, "w", encoding="utf-8").write(src)
            print("[p10] MainActivity modern Android UI uygulandi:", mp)

HUD_APPEND_PY2 = '''
# === SALTANAT_HUD_V10_SAFE ===
try:
    import ui as _sh_ui, wndMgr as _sh_wnd, player as _sh_player, net as _sh_net

    class _SaltanatGlassBtn(_sh_ui.Window):
        def __init__(self, parent, x, y, w, h, label, bg=0xBB101622, border=0xFFD4AF37, cb=None):
            _sh_ui.Window.__init__(self)
            if parent is not None:
                self.SetParent(parent)
            self.SetPosition(x, y)
            self.SetSize(w, h)
            self._cb = cb
            self._bg = bg
            self._fill = _sh_ui.Bar()
            self._fill.SetParent(self)
            self._fill.AddFlag("not_pick")
            self._fill.SetPosition(0, 0)
            self._fill.SetSize(w, h)
            self._fill.SetColor(bg)
            self._fill.Show()
            self._border = _sh_ui.Box()
            self._border.SetParent(self)
            self._border.AddFlag("not_pick")
            self._border.SetPosition(0, 0)
            self._border.SetSize(w, h)
            self._border.SetColor(border)
            self._border.Show()
            self._txt = _sh_ui.TextLine()
            self._txt.SetParent(self)
            self._txt.AddFlag("not_pick")
            self._txt.SetPosition(w // 2, h // 2)
            self._txt.SetHorizontalAlignCenter()
            self._txt.SetVerticalAlignCenter()
            self._txt.SetPackedFontColor(0xFFF5E6C4)
            self._txt.SetText(label)
            self._txt.Show()
            if parent is not None:
                self.Show()
            else:
                self.Hide()

        def OnMouseLeftButtonDown(self):
            try:
                self._fill.SetColor(0xDD2A364B)
            except Exception:
                pass
            if self._cb:
                try:
                    self._cb()
                except Exception:
                    pass
            return True

        def OnMouseLeftButtonUp(self):
            try:
                self._fill.SetColor(self._bg)
            except Exception:
                pass
            return True

    class SaltanatMobileHUD(_sh_ui.Window):
        def __init__(self, *args, **kwargs):
            _sh_ui.Window.__init__(self)
            self.interface = args[0] if args else kwargs.get("interface", None)
            self.menuOpen = False
            self._widgets = []
            self.menuBtns = []
            self.drawer = None
            self._built = False
            self.SetSize(0, 0)
            self.SetPosition(0, 0)

        def BindInterface(self, interface):
            self.interface = interface

        def SetInterface(self, interface):
            self.interface = interface

        def Build(self):
            if self._built:
                return
            sw = _sh_wnd.GetScreenWidth()
            sh = _sh_wnd.GetScreenHeight()
            if sw <= 0 or sh <= 0:
                return
            self._built = True

            self.menuToggle = _SaltanatGlassBtn(None, sw - 96, 12, 84, 34, "MENU", 0xCC121824, 0xFFD4AF37, self.ToggleMenu)
            self._widgets.append(self.menuToggle)

            self.drawer = _sh_ui.Window()
            self.drawer.SetPosition(sw - 134, 52)
            self.drawer.SetSize(122, 248)
            self._drawerBg = _sh_ui.Bar()
            self._drawerBg.SetParent(self.drawer)
            self._drawerBg.AddFlag("not_pick")
            self._drawerBg.SetPosition(0, 0)
            self._drawerBg.SetSize(122, 248)
            self._drawerBg.SetColor(0xEE0D121C)
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
                b = _SaltanatGlassBtn(self.drawer, 6, 6 + idx * 34, 110, 30, lbl, 0xBB182235, 0xAA9E8242, fn)
                self.menuBtns.append(b)

            self.atkBtn = _SaltanatGlassBtn(None, sw - 92, sh - 92, 76, 76, "SALDIRI", 0xCC7A1C1C, 0xFFE6C15A, self._attack_tap)
            self.pickBtn = _SaltanatGlassBtn(None, sw - 166, sh - 46, 66, 32, "TOPLA", 0xBB162820, 0xFF66BB6A, self._pickup)
            self.mntBtn = _SaltanatGlassBtn(None, sw - 166, sh - 84, 66, 32, "BINEK", 0xBB1C2236, 0xFFD4AF37, self._mount)
            self._widgets.extend([self.atkBtn, self.pickBtn, self.mntBtn])

            coords = [
                (sw - 236, sh - 52), (sw - 236, sh - 102), (sw - 186, sh - 138), (sw - 132, sh - 148),
                (sw - 78, sh - 148), (sw - 288, sh - 52), (sw - 288, sh - 102), (sw - 242, sh - 150)
            ]
            labels = ["1", "2", "3", "4", "F1", "F2", "F3", "F4"]
            for i in range(8):
                x, y = coords[i]
                btn = _SaltanatGlassBtn(None, x, y, 44, 44, labels[i], 0xBB101828, 0xFFC8A24A, lambda s=i: self._use_slot(s))
                self._widgets.append(btn)

        def ToggleMenu(self):
            if not self._built:
                self.Build()
            self.menuOpen = not self.menuOpen
            if self.drawer:
                if self.menuOpen:
                    self.drawer.Show()
                    self.drawer.SetTop()
                else:
                    self.drawer.Hide()

        def _use_slot(self, idx):
            try:
                _sh_player.RequestUseLocalQuickSlot(idx)
            except Exception:
                pass

        def _attack_tap(self):
            try:
                _sh_player.SetAttackKeyState(True)
                _sh_player.SetAttackKeyState(False)
            except Exception:
                pass

        def _pickup(self):
            try:
                _sh_player.PickCloseItem()
            except Exception:
                pass

        def _mount(self):
            try:
                _sh_net.SendChatPacket("/user_horse_ride")
            except Exception:
                pass
            try:
                _sh_net.SendChatPacket("/mount_test 20240")
            except Exception:
                pass

        def _pet(self):
            try:
                for slot in range(90):
                    v = _sh_player.GetItemIndex(slot)
                    if v in (53001, 53002, 53003, 53005, 53006, 53007, 53008, 53009, 53010):
                        _sh_net.SendItemUsePacket(slot)
                        return
                _sh_net.SendChatPacket("/m 34001")
            except Exception:
                pass

        def _warp_town(self):
            if self.menuOpen:
                self.ToggleMenu()
            try:
                _sh_net.SendChatPacket("/go c")
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
            if not self._built:
                try:
                    self.Build()
                except Exception:
                    pass
            _sh_ui.Window.Show(self)
            for w in self._widgets:
                try:
                    w.Show()
                except Exception:
                    pass

        def Hide(self):
            _sh_ui.Window.Hide(self)
            for w in self._widgets:
                try:
                    w.Hide()
                except Exception:
                    pass
            if self.drawer:
                self.drawer.Hide()
            self.menuOpen = False

        def Open(self):
            self.Show()

        def Close(self):
            self.Hide()

        def Destroy(self):
            self.Hide()
            self._widgets = []
            self.menuBtns = []
            self.drawer = None

        def OnUpdate(self):
            pass

        def Refresh(self):
            pass

        def __getattr__(self, name):
            return lambda *a, **kw: None
except Exception:
    pass
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
            bg.SetParent(self); bg.AddFlag(
