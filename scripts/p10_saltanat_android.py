#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, re, shutil, sqlite3, subprocess, sys, urllib.request, zipfile

REL_REPO = "zenfasulyesi55-afk/Metin2-Lab"
BUNDLE_URL = "https://github.com/%s/releases/download/saltanat-assets-v1/saltanat_kraliyet_bundle.zip" % REL_REPO
BUNDLE_LOCAL = "/tmp/saltanat_kraliyet_bundle.zip"
HUD_M = "# === SALTANAT_HUD_V10_SAFE ==="
INV_M = "# === SALTANAT_INV_V10 ==="
SHP_M = "# === SALTANAT_SHOP_V10 ==="
LOG_M = "# === SALTANAT_LOGIN_V10 ==="

def _find(names):
    if isinstance(names, str): names = (names,)
    low = {n.lower() for n in names}
    hits = []
    for base in ("client-src", "server-src", "/tmp/m2stage", "/tmp/m2serverpack", "."):
        if not os.path.isdir(base): continue
        for r, ds, fs in os.walk(base):
            ds[:] = [d for d in ds if d not in (".git", "build", ".gradle")]
            for f in fs:
                if f.lower() in low:
                    p = os.path.abspath(os.path.join(r, f))
                    if p not in hits: hits.append(p)
    return hits

def _bal(s): return s.count("{") == s.count("}") and s.count("(") == s.count(")")

def ensure_bundle():
    if os.path.isfile(BUNDLE_LOCAL) and zipfile.is_zipfile(BUNDLE_LOCAL): return BUNDLE_LOCAL
    print("[p10] Saltanat paketi indiriliyor...")
    try:
        urllib.request.urlretrieve(BUNDLE_URL, BUNDLE_LOCAL)
        if zipfile.is_zipfile(BUNDLE_LOCAL): return BUNDLE_LOCAL
    except Exception: pass
    subprocess.run(["gh", "release", "download", "saltanat-assets-v1", "-R", REL_REPO,
                    "-p", "saltanat_kraliyet_bundle.zip", "-D", "/tmp", "--clobber"], check=False)
    return BUNDLE_LOCAL if os.path.isfile(BUNDLE_LOCAL) and zipfile.is_zipfile(BUNDLE_LOCAL) else None

def patch_java():
    for jp in _find("JoystickView.java"):
        src = open(jp, encoding="utf-8", errors="ignore").read()
        if "SALTANAT_DYN_JOY_V10" in src: continue
        orig = src
        src = re.sub(r"Color\.argb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)", "0x66121722", src, count=1)
        src = re.sub(r"new\s+Paint\s*\(\s*\)", "new Paint(Paint.ANTI_ALIAS_FLAG)", src)
        cx = next((n for n in ("centerX", "mCenterX", "baseX", "cx") if re.search(r"\b"+n+r"\b", src)), None)
        cy = next((n for n in ("centerY", "mCenterY", "baseY", "cy") if re.search(r"\b"+n+r"\b", src)), None)
        if cx and cy and "ACTION_DOWN" in src:
            d = "/* SALTANAT_DYN_JOY_V10 */ setAlpha(1.0f); float _p=Math.min(getWidth(),getHeight())*0.28f; %s=Math.max(_p,Math.min(getWidth()-_p,event.getX())); %s=Math.max(_p,Math.min(getHeight()-_p,event.getY()));" % (cx, cy)
            src = re.sub(r"(case\s+MotionEvent\.ACTION_DOWN\s*:)", r"\1 " + d, src, count=1)
            src = re.sub(r"(case\s+MotionEvent\.ACTION_UP\s*:)", r"\1 setAlpha(0.32f);", src, count=1)
        if _bal(src) and src != orig:
            open(jp, "w", encoding="utf-8").write(src); print("[p10] JoystickView dinamik:", jp)
    for mp in _find("MainActivity.java"):
        src = open(mp, encoding="utf-8", errors="ignore").read()
        if "SALTANAT_UI_V10B" in src: continue
        orig = src
        imm = (" /* SALTANAT_UI_V10B */ try { getWindow().getDecorView().setBackgroundColor(0xFF0A0D14);"
               " getWindow().getDecorView().setSystemUiVisibility(4096|4|2|256|1024|512); } catch (Throwable _e) {} ")
        src = re.sub(r"(super\.onCreate\s*\([^)]*\)\s*;)", r"\1" + imm, src, count=1)
        src = src.replace("0xFF1A1A2E", "0xFF0C1018").replace("0xFF16213E", "0xFF121926")
        if _bal(src) and src != orig:
            open(mp, "w", encoding="utf-8").write(src); print("[p10] MainActivity UI:", mp)

HUD_PY2 = '''
# === SALTANAT_HUD_V10_SAFE ===
try:
    import ui as _su, wndMgr as _sw, player as _sp, net as _sn
    class _SBtn(_su.Window):
        def __init__(self, p, x, y, w, h, lbl, bg=0xBB101622, bd=0xFFD4AF37, cb=None):
            _su.Window.__init__(self)
            if p is not None: self.SetParent(p)
            self.SetPosition(x, y); self.SetSize(w, h); self._cb = cb; self._bg = bg
            f = _su.Bar(); f.SetParent(self); f.AddFlag("not_pick"); f.SetPosition(0,0); f.SetSize(w,h); f.SetColor(bg); f.Show()
            b = _su.Box(); b.SetParent(self); b.AddFlag("not_pick"); b.SetPosition(0,0); b.SetSize(w,h); b.SetColor(bd); b.Show()
            t = _su.TextLine(); t.SetParent(self); t.AddFlag("not_pick"); t.SetPosition(w//2,h//2)
            t.SetHorizontalAlignCenter(); t.SetVerticalAlignCenter(); t.SetPackedFontColor(0xFFF5E6C4); t.SetText(lbl); t.Show()
            self._f = f; self._p = (b, t)
            if p is not None: self.Show()
            else: self.Hide()
        def OnMouseLeftButtonDown(self):
            try: self._f.SetColor(0xDD2A364B)
            except Exception: pass
            if self._cb:
                try: self._cb()
                except Exception: pass
            return True
        def OnMouseLeftButtonUp(self):
            try: self._f.SetColor(self._bg)
            except Exception: pass
            return True

    class SaltanatMobileHUD(_su.Window):
        def __init__(self, *a, **kw):
            _su.Window.__init__(self)
            self.interface = a[0] if a else kw.get("interface", None)
            self.menuOpen = False; self._ws = []; self._mb = []; self.drawer = None; self._ok = False
            self.SetSize(0, 0); self.SetPosition(0, 0)
        def BindInterface(self, i): self.interface = i
        def SetInterface(self, i): self.interface = i
        def Build(self):
            if self._ok: return
            sw, sh = _sw.GetScreenWidth(), _sw.GetScreenHeight()
            if sw <= 0 or sh <= 0: return
            self._ok = True
            self._ws.append(_SBtn(None, sw-96, 12, 84, 34, "MENU", 0xCC121824, 0xFFD4AF37, self.ToggleMenu))
            self.drawer = _su.Window(); self.drawer.SetPosition(sw-134, 52); self.drawer.SetSize(122, 248)
            bg = _su.Bar(); bg.SetParent(self.drawer); bg.AddFlag("not_pick"); bg.SetPosition(0,0); bg.SetSize(122,248); bg.SetColor(0xEE0D121C); bg.Show()
            self._dbg = bg; self.drawer.Hide()
            items = [("Envanter", self._inv), ("Karakter", self._chr), ("Beceriler", self._skl),
                     ("Sohbet", self._cht), ("Binek Bin", self._mnt), ("Pet Cagir", self._pet), ("Sehir Don", self._wrp)]
            for idx, (lbl, fn) in enumerate(items):
                self._mb.append(_SBtn(self.drawer, 6, 6+idx*34, 110, 30, lbl, 0xBB182235, 0xAA9E8242, fn))
            self._ws.extend([
                _SBtn(None, sw-92, sh-92, 76, 76, "SALDIRI", 0xCC7A1C1C, 0xFFE6C15A, self._atk),
                _SBtn(None, sw-166, sh-46, 66, 32, "TOPLA", 0xBB162820, 0xFF66BB6A, self._pck),
                _SBtn(None, sw-166, sh-84, 66, 32, "BINEK", 0xBB1C2236, 0xFFD4AF37, self._mnt),
            ])
            xy = [(sw-236,sh-52),(sw-236,sh-102),(sw-186,sh-138),(sw-132,sh-148),(sw-78,sh-148),(sw-288,sh-52),(sw-288,sh-102),(sw-242,sh-150)]
            lb = ["1","2","3","4","F1","F2","F3","F4"]
            for i in range(8):
                self._ws.append(_SBtn(None, xy[i][0], xy[i][1], 44, 44, lb[i], 0xBB101828, 0xFFC8A24A, lambda s=i: self._slt(s)))
        def ToggleMenu(self):
            if not self._ok: self.Build()
            self.menuOpen = not self.menuOpen
            if self.drawer:
                if self.menuOpen: self.drawer.Show(); self.drawer.SetTop()
                else: self.drawer.Hide()
        def _slt(self, i):
            try: _sp.RequestUseLocalQuickSlot(i)
            except Exception: pass
        def _atk(self):
            try: _sp.SetAttackKeyState(True); _sp.SetAttackKeyState(False)
            except Exception: pass
        def _pck(self):
            try: _sp.PickCloseItem()
            except Exception: pass
        def _mnt(self):
            for c in ("/user_horse_ride", "/mount_test 20240"):
                try: _sn.SendChatPacket(c)
                except Exception: pass
        def _pet(self):
            try:
                for s in range(90):
                    if _sp.GetItemIndex(s) in (53001,53002,53003,53005,53006,53007,53008,53009,53010):
                        _sn.SendItemUsePacket(s); return
                _sn.SendChatPacket("/m 34001")
            except Exception: pass
        def _wrp(self):
            if self.menuOpen: self.ToggleMenu()
            try: _sn.SendChatPacket("/go c")
            except Exception: pass
        def _inv(self):
            if self.menuOpen: self.ToggleMenu()
            try:
                if self.interface: self.interface.ToggleInventoryWindow()
            except Exception: pass
        def _chr(self):
            if self.menuOpen: self.ToggleMenu()
            try:
                if self.interface: self.interface.ToggleCharacterWindow("STATUS")
            except Exception: pass
        def _skl(self):
            if self.menuOpen: self.ToggleMenu()
            try:
                if self.interface: self.interface.ToggleCharacterWindow("SKILL")
            except Exception: pass
        def _cht(self):
            if self.menuOpen: self.ToggleMenu()
            try:
                if self.interface and hasattr(self.interface, "ToggleChat"): self.interface.ToggleChat()
            except Exception: pass
        def Show(self):
            if not self._ok:
                try: self.Build()
                except Exception: pass
            _su.Window.Show(self)
            for w in self._ws:
                try: w.Show()
                except Exception: pass
        def Hide(self):
            _su.Window.Hide(self)
            for w in self._ws:
                try: w.Hide()
                except Exception: pass
            if self.drawer: self.drawer.Hide()
            self.menuOpen = False
        def Open(self): self.Show()
        def Close(self): self.Hide()
        def Destroy(self): self.Hide(); self._ws = []; self._mb = []; self.drawer = None
        def OnUpdate(self): pass
        def Refresh(self): pass
        def __getattr__(self, n): return lambda *a, **kw: None
except Exception:
    pass
'''

INV_PY2 = '''
# === SALTANAT_INV_V10 ===
try:
    import time as _it, ui as _iu, net as _in, player as _ip, wndMgr as _iw
    class _ITBtn(_iu.Window):
        def __init__(self, p, x, y, w, h, lbl, col, fn):
            _iu.Window.__init__(self); self.SetParent(p); self.SetPosition(x,y); self.SetSize(w,h); self._fn = fn
            b = _iu.Bar(); b.SetParent(self); b.AddFlag("not_pick"); b.SetPosition(0,0); b.SetSize(w,h); b.SetColor(col); b.Show()
            t = _iu.TextLine(); t.SetParent(self); t.AddFlag("not_pick"); t.SetPosition(w//2,h//2)
            t.SetHorizontalAlignCenter(); t.SetVerticalAlignCenter(); t.SetPackedFontColor(0xFFF5E6C4); t.SetText(lbl); t.Show()
            self._p = (b, t); self.Show()
        def OnMouseLeftButtonDown(self):
            try: self._fn()
            except Exception: pass
            return True
    class _IABar(_iu.Window):
        def __init__(self):
            _iu.Window.__init__(self); sw, sh = _iw.GetScreenWidth(), _iw.GetScreenHeight()
            self.SetSize(316, 48); self.SetPosition((sw-316)//2, sh-62); self.slot = -1
            b = _iu.Bar(); b.SetParent(self); b.AddFlag("not_pick"); b.SetPosition(0,0); b.SetSize(316,48); b.SetColor(0xEE0E1420); b.Show()
            self._b = b
            self._bs = [_ITBtn(self, 6,6,96,36,"KULLAN/GIY",0xCC1E5631,self._u), _ITBtn(self,108,6,92,36,"SLOTA KOY",0xCC1B3B6F,self._q),
                        _ITBtn(self,206,6,66,36,"SAT/AT",0xCC6E2626,self._d), _ITBtn(self,278,6,32,36,"X",0xCC333A48,self.Hide)]
            self.Hide()
        def OpenFor(self, s): self.slot = s; self.Show(); self.SetTop()
        def _u(self):
            try: _in.SendItemUsePacket(self.slot)
            except Exception: pass
            self.Hide()
        def _q(self):
            try:
                for i in range(8):
                    if _ip.GetLocalQuickSlot(i)[0] == 0:
                        _ip.RequestAddLocalQuickSlot(i, _ip.SLOT_TYPE_INVENTORY, self.slot); break
            except Exception: pass
            self.Hide()
        def _d(self):
            try: _in.SendItemDropPacketNew(self.slot, 1)
            except Exception:
                try: _in.SendItemDropPacket(self.slot)
                except Exception: pass
            self.Hide()
    _IB = None; _IL = [-1, 0.0]
    if "InventoryWindow" in globals() and hasattr(InventoryWindow, "SelectItemSlot"):
        _os = InventoryWindow.SelectItemSlot
        def _as(self, idx):
            global _IB
            try:
                now = _it.time()
                s = self._InventoryWindow__InventoryLocalSlotPosToGlobalSlotPos(idx) if hasattr(self, "_InventoryWindow__InventoryLocalSlotPosToGlobalSlotPos") else idx
                if _IL[0] == s and (now - _IL[1]) < 0.45:
                    _IL[0] = -1
                    if _IB: _IB.Hide()
                    _in.SendItemUsePacket(s); return
                _IL[0] = s; _IL[1] = now
                if _IB is None: _IB = _IABar()
                _IB.OpenFor(s)
            except Exception: pass
            return _os(self, idx)
        InventoryWindow.SelectItemSlot = _as
except Exception:
    pass
'''

SHP_PY2 = '''
# === SALTANAT_SHOP_V10 ===
try:
    import time as _qt, ui as _qu, net as _qn, wndMgr as _qw
    class _QBtn(_qu.Window):
        def __init__(self, p, x, y, w, h, lbl, col, fn):
            _qu.Window.__init__(self); self.SetParent(p); self.SetPosition(x,y); self.SetSize(w,h); self._fn = fn
            b = _qu.Bar(); b.SetParent(self); b.AddFlag("not_pick"); b.SetPosition(0,0); b.SetSize(w,h); b.SetColor(col); b.Show()
            t = _qu.TextLine(); t.SetParent(self); t.AddFlag("not_pick"); t.SetPosition(w//2,h//2)
            t.SetHorizontalAlignCenter(); t.SetVerticalAlignCenter(); t.SetPackedFontColor(0xFFF5E6C4); t.SetText(lbl); t.Show()
            self._p = (b, t); self.Show()
        def OnMouseLeftButtonDown(self):
            try: self._fn()
            except Exception: pass
            return True
    class _QBar(_qu.Window):
        def __init__(self):
            _qu.Window.__init__(self); sw, sh = _qw.GetScreenWidth(), _qw.GetScreenHeight()
            self.SetSize(224, 48); self.SetPosition((sw-224)//2, sh-62); self.slot = -1
            b = _qu.Bar(); b.SetParent(self); b.AddFlag("not_pick"); b.SetPosition(0,0); b.SetSize(224,48); b.SetColor(0xEE0E1420); b.Show()
            self._b = b
            self._bs = [_QBtn(self,6,6,136,36,"SATIN AL",0xCC1E5631,self._buy), _QBtn(self,148,6,70,36,"IPTAL",0xCC4A2020,self.Hide)]
            self.Hide()
        def OpenFor(self, s): self.slot = s; self.Show(); self.SetTop()
        def _buy(self):
            try: _qn.SendShopBuyPacket(self.slot)
            except Exception: pass
            self.Hide()
    _QB = None; _QL = [-1, 0.0]
    if "ShopDialog" in globals() and hasattr(ShopDialog, "SelectItemSlot"):
        _oq = ShopDialog.SelectItemSlot
        def _aq(self, pos):
            global _QB
            try:
                now = _qt.time()
                if _QL[0] == pos and (now - _QL[1]) < 0.45:
                    _QL[0] = -1
                    if _QB: _QB.Hide()
                    _qn.SendShopBuyPacket(pos); return
                _QL[0] = pos; _QL[1] = now
                if _QB is None: _QB = _QBar()
                _QB.OpenFor(pos)
            except Exception: pass
            return _oq(self, pos)
        ShopDialog.SelectItemSlot = _aq
except Exception:
    pass
'''

LOG_PY2 = '''
# === SALTANAT_LOGIN_V10 ===
try:
    import ui as _lu, wndMgr as _lw
    if "LoginWindow" in globals() and hasattr(LoginWindow, "Open"):
        _olo = LoginWindow.Open
        def _alo(self):
            r = _olo(self)
            try:
                if not hasattr(self, "_shdr"):
                    sw, sh = _lw.GetScreenWidth(), _lw.GetScreenHeight()
                    h = _lu.Bar(); h.SetSize(280,34); h.SetPosition((sw-280)//2,10); h.SetColor(0xCC0D121C); h.AddFlag("not_pick"); h.Show()
                    ht = _lu.TextLine(); ht.SetParent(h); ht.AddFlag("not_pick"); ht.SetPosition(140,17)
                    ht.SetHorizontalAlignCenter(); ht.SetVerticalAlignCenter(); ht.SetPackedFontColor(0xFFE6C15A); ht.SetText("SALTANAT METIN2 - ANDROID"); ht.Show()
                    q = _lu.Window(); q.SetSize(168,42); q.SetPosition((sw-168)//2, sh-54)
                    qb = _lu.Bar(); qb.SetParent(q); qb.AddFlag("not_pick"); qb.SetPosition(0,0); qb.SetSize(168,42); qb.SetColor(0xDD1A4D2E); qb.Show()
                    qx = _lu.Box(); qx.SetParent(q); qx.AddFlag("not_pick"); qx.SetPosition(0,0); qx.SetSize(168,42); qx.SetColor(0xFFD4AF37); qx.Show()
                    qt = _lu.TextLine(); qt.SetParent(q); qt.AddFlag("not_pick"); qt.SetPosition(84,21)
                    qt.SetHorizontalAlignCenter(); qt.SetVerticalAlignCenter(); qt.SetPackedFontColor(0xFFF5E6C4); qt.SetText("HIZLI GIRIS"); qt.Show()
                    def _go():
                        for m in ("_LoginWindow__OnClickLoginButton", "OnClickLoginButton"):
                            if hasattr(self, m): getattr(self, m)(); break
                    q.OnMouseLeftButtonDown = (lambda: (_go(), True)[1]); q.Show()
                    self._shdr = (h, ht, q, qb, qx, qt)
            except Exception: pass
            return r
        LoginWindow.Open = _alo
        if hasattr(LoginWindow, "Close"):
            _olc = LoginWindow.Close
            def _alc(self):
                try:
                    for w in getattr(self, "_shdr", ()):
                        if hasattr(w, "Hide"): w.Hide()
                except Exception: pass
                return _olc(self)
            LoginWindow.Close = _alc
except Exception:
    pass
'''

def patch_py():
    skip = ("opt","gfx","cfg","conf","dlg","dialog","set","btn","bar","slider","dev","panel")
    for hp in _find("uimobilehud.py"):
        o = open(hp, encoding="utf-8", errors="ignore").read().split(HUD_M)[0].rstrip()
        cls = [c for c in re.findall(r"^class\s+(\w+)", o, re.M) if ("hud" in c.lower() or "mobile" in c.lower()) and not any(w in c.lower() for w in skip)]
        if "MobileHUD" not in cls: cls.append("MobileHUD")
        al = "\n".join("%s = SaltanatMobileHUD" % c for c in sorted(set(cls)) if c != "SaltanatMobileHUD")
        open(hp, "w", encoding="utf-8").write(o + "\n\n" + HUD_PY2.strip() + "\n" + al + "\n")
        print("[p10] uimobilehud OK:", hp)
    for fn, mk, code in (("uiinventory.py", INV_M, INV_PY2), ("uishop.py", SHP_M, SHP_PY2), ("intrologin.py", LOG_M, LOG_PY2)):
        for p in _find(fn):
            t = open(p, encoding="utf-8", errors="ignore").read().split(mk)[0].rstrip()
            open(p, "w", encoding="utf-8").write(t + "\n" + code)
            print("[p10] %s OK:" % fn, p)

def patch_server():
    for cp in _find("CONFIG"):
        t = open(cp, encoding="utf-8", errors="ignore").read()
        nt = re.sub(r"(?im)^MAX_LEVEL\s*:\s*\d+", "MAX_LEVEL: 300", t) if re.search(r"(?im)^MAX_LEVEL\s*:", t) else t.rstrip() + "\nMAX_LEVEL: 300\n"
        if nt != t: open(cp, "w", encoding="utf-8").write(nt); print("[p10] CONFIG 300:", cp)
    for dbp in _find(("player.sqlite", "player.sqlite3")):
        try:
            con = sqlite3.connect(dbp); cur = con.cursor()
            ts = {r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if "shop" in ts and "shop_item" in ts:
                cur.execute("INSERT OR IGNORE INTO shop (vnum, name, npc_vnum) VALUES (900, 'Saltanat Market', 20400)")
                for r in ((900,19,1),(900,149,1),(900,299,1),(900,11299,1),(900,71124,1),(900,53001,1),(900,27992,5),(900,27993,5),(900,27994,5)):
                    cur.execute("INSERT OR IGNORE INTO shop_item (shop_vnum, item_vnum, count) VALUES (?,?,?)", r)
            if "refine_proto" in ts:
                cur.execute("UPDATE refine_proto SET prob = 100 WHERE prob < 100")
                        con.commit(); con.close(); print("[p10] SQLite OK:", dbp)
        except Exception as e: print("[p10] SQLite uyari:", e)

def apply_bundle():
    bp = ensure_bundle()
    if not bp: return
    zf = zipfile.ZipFile(bp); ns = set(zf.namelist())
    for base in ("/tmp/m2serverpack/server", "/tmp/m2serverpack"):
        if not os.path.isdir(base): continue
        for r, _, fs in os.walk(base):
            for f in fs:
                k = "server/data/" + f.lower()
                if f.lower() in ("mob_drop_item.txt", "special_item_group.txt") and k in ns:
                    open(os.path.join(r, f), "wb").write(zf.read(k))
    st = "/tmp/m2stage"
    if os.path.isdir(st):
        for mp in ("metin2_map_a1", "metin2_map_b1", "metin2_map_c1"):
            shutil.rmtree(os.path.join(st, mp), ignore_errors=True)
        n = 0
        for info in zf.infolist():
            if info.is_dir(): continue
            fn = info.filename
            rel = fn[12:] if fn.startswith("client/maps/") else (fn[7:] if fn.startswith(("client/icon/", "client/a_maviruhkraliyet")) else None)
            if not rel: continue
            tp = os.path.join(st, rel); os.makedirs(os.path.dirname(tp), exist_ok=True)
            open(tp, "wb").write(zf.read(info)); n += 1
        for mp in ("metin2_map_a1", "metin2_map_b1", "metin2_map_c1"):
            sp = os.path.join(st, mp, "setting.txt")
            if os.path.isfile(sp):
                open(sp, "w", encoding="utf-8").write(re.sub(r"(?im)^Environment\s+.*$", "Environment\ta1.msenv", open(sp, encoding="utf-8", errors="ignore").read()))
        print("[p10] Harita/varlik OK:", n)

def run(stage_only=False):
    if not stage_only: patch_java()
    patch_py(); patch_server(); apply_bundle()

if __name__ == "__main__":
    run("--stage-only" in sys.argv)
    
