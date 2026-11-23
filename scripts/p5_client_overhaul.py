import os, re
ROOT = "client-src/r10dev.net OPENGL-ITJA"
rd = lambda p: open(p, "r", encoding="utf-8", errors="ignore").read()
wr = lambda p, s: open(p, "w", encoding="utf-8").write(s)

def patch_cpp_core():
    p = os.path.join(ROOT, "clientsource/UserInterface/AndroidMain.cpp")
    if os.path.isfile(p) and "MIKO_FPS_EGL_V1" not in rd(p):
        s = rd(p)
        hlp = """
// MIKO_FPS_EGL_V1
#include <time.h>
static int s_mikoFps = 60, s_mikoGfx = 2, s_mikoShop = 1;
static unsigned long s_mikoFrm = 0; static long long s_mikoLastNs = 0;
static void MikoLoadCfg() {
    FILE* f = fopen("m2_gfx.cfg", "r"); if (!f) return; char b[96]; int v = 0;
    while (fgets(b, sizeof(b), f)) {
        if (sscanf(b, "fps=%d", &v) == 1 && (v==30||v==60||v==120)) s_mikoFps = v;
        else if (sscanf(b, "gfx=%d", &v) == 1 && v>=0 && v<=2) s_mikoGfx = v;
        else if (sscanf(b, "shop_names=%d", &v) == 1) s_mikoShop = v ? 1 : 0;
    } fclose(f);
}
static void MikoPace(EGLDisplay d) {
    if ((s_mikoFrm++ % 60) == 0) { MikoLoadCfg(); if (d != EGL_NO_DISPLAY) eglSwapInterval(d, s_mikoFps >= 90 ? 0 : 1); }
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts);
    long long now = (long long)ts.tv_sec * 1000000000LL + ts.tv_nsec;
    long long tgt = 1000000000LL / (s_mikoFps > 0 ? s_mikoFps : 60);
    if (s_mikoLastNs > 0 && (now - s_mikoLastNs) < tgt) {
        long long us = (tgt - (now - s_mikoLastNs)) / 1000LL;
        if (us > 200 && us < 50000) usleep((useconds_t)us);
        clock_gettime(CLOCK_MONOTONIC, &ts); now = (long long)ts.tv_sec * 1000000000LL + ts.tv_nsec;
    } s_mikoLastNs = now;
}
extern "C" int MikoGetTargetFps() { return s_mikoFps; }
"""
        m = re.search(r"(#include[^\n]+\n)(?!#include)", s)
        s = (s[:m.end()] + hlp + s[m.end():]) if m else (hlp + s)
        s = s.replace("usleep(33000);", "MikoPace(s_eglDisplay);").replace("EGL_DEPTH_SIZE, 16,", "EGL_DEPTH_SIZE, 24,")
        wr(p, s)
    pa = os.path.join(ROOT, "clientsource/UserInterface/PythonApplication.cpp")
    if os.path.isfile(pa) and "MIKO_APP_FPS_V1" not in rd(pa):
        wr(pa, 'extern "C" int MikoGetTargetFps();\n// MIKO_APP_FPS_V1\n' + rd(pa).replace("m_iFPS = 60;", "m_iFPS = MikoGetTargetFps();"))
    tt = os.path.join(ROOT, "clientsource/UserInterface/PythonTextTail.cpp")
    if os.path.isfile(tt) and "MIKO_DROP_OPT_V1" not in rd(tt):
        s = "// MIKO_DROP_OPT_V1\nstatic unsigned int s_mikoTT = 0;\n" + rd(tt)
        s = re.sub(r"(void\s+CPythonTextTail::ArrangeTextTail\s*\(\s*\)\s*\{)", r"\1\n\tif (m_ItemTextTailList.size() > 14 && (++s_mikoTT % 4) != 0) return;\n", s, count=1)
        wr(tt, s)
    ef = os.path.join(ROOT, "clientsource/UserInterface/InstanceBaseEffect.cpp")
    if os.path.isfile(ef) and "MIKO_PLUS9_V1" not in rd(ef):
        s = re.sub(r"(case\s+9\s*:[\s\S]{0,220}?__AttachEffect\s*\(\s*([^)]+)\s*\)\s*;)", r"\1\n\t\t\t\t/* MIKO_PLUS9_V1 */ __AttachEffect(\2);", rd(ef), count=2)
        wr(ef, s)
    for r, _, fs in os.walk(os.path.join(ROOT, "clientsource")):
        for fn in fs:
            if fn.endswith((".cpp", ".c")):
                fp = os.path.join(r, fn); s = rd(fp)
                if "GL_TEXTURE_MIN_FILTER" in s and "MIKO_ANISO_V1" not in s:
                    s2 = s.replace("GL_NEAREST_MIPMAP_NEAREST", "GL_LINEAR_MIPMAP_LINEAR").replace("GL_LINEAR_MIPMAP_NEAREST", "GL_LINEAR_MIPMAP_LINEAR")
                    if s2 != s: wr(fp, "// MIKO_ANISO_V1\n" + s2)

def patch_hud_and_options():
    art = os.path.join(ROOT, "android/tools/data-overlay/make_hud_art.py")
    if os.path.isfile(art) and "MIKO_GLASS_V1" not in rd(art):
        s = "# MIKO_GLASS_V1\n" + rd(art)
        for a, b in ((r"\(\s*18\s*,\s*16\s*,\s*14\s*,","(14, 17, 23,"),(r"\(\s*24\s*,\s*20\s*,\s*16\s*,","(16, 20, 27,"),(r"\(\s*200\s*,\s*170\s*,\s*105\s*,","(196, 178, 140,")):
            s = re.sub(a, b, s)
        wr(art, s)
    hud = os.path.join(ROOT, "android/tools/data-overlay/uimobilehud.py")
    if os.path.isfile(hud) and "MIKO_HUD_V1" not in rd(hud):
        s = rd(hud) + '''
# MIKO_HUD_V1
def LoadGfxConfig():
    c = {"fps": 60, "gfx": 2, "shop_names": 1, "hud_scale": 100}
    try:
        for ln in open("m2_gfx.cfg"):
            if "=" in ln:
                k, v = ln.strip().split("=", 1)
                if k in c: c[k] = int(v)
    except Exception: pass
    return c
def SaveGfxConfig(c):
    try:
        f = open("m2_gfx.cfg", "w")
        for k in ("fps", "gfx", "shop_names", "hud_scale"): f.write("%s=%d\\n" % (k, int(c.get(k, 0))))
        f.close()
    except Exception: pass
    ApplyGfxLive(c)
def ApplyGfxLive(c):
    try:
        import systemSetting, background
        p = int(c.get("gfx", 2))
        if hasattr(systemSetting, "SetShowSalesTextFlag"): systemSetting.SetShowSalesTextFlag(bool(c.get("shop_names", 1)))
        if hasattr(systemSetting, "SetShadowLevel"): systemSetting.SetShadowLevel(5 if p==2 else (3 if p==1 else 0))
        if hasattr(systemSetting, "SetFogMode"): systemSetting.SetFogMode(False if p==2 else True)
        if hasattr(background, "SetViewDistanceSet"): background.SetViewDistanceSet(0, 25600 if p==2 else (16000 if p==1 else 9600))
    except Exception: pass
'''
        s = re.sub(r"(def __SlotIcon\(self,\s*index\):[\s\S]{0,600}?SetScale\s*\()\s*([0-9.]+)\s*,\s*([0-9.]+)\s*(\))", r"\g<1>1.34, 1.34\g<4>", s, count=2)
        s = re.sub(r"(class MobileHud\(ui\.Window\):[\s\S]{0,200}?def __init__\(self[^)]*\):)", r"\1\n        try: ApplyGfxLive(LoadGfxConfig())\n        except Exception: pass", s, count=1)
        m_a = re.search(r"(def __Attack\(self\):[\s\S]{0,360}?)(?=\n    def )", s)
        if m_a:
            s = s.replace(m_a.group(1), "def __Attack(self):\n        try: player.SetAttackKeyState(True)\n        except Exception: pass\n", 1)
        wr(hud, s)
    opt = os.path.join(ROOT, "android/tools/data-overlay/uidevoptions.py")
    if os.path.isfile(opt) and "MIKO_OPT_V1" not in rd(opt) and "self.closeBtn = _MakeButton" in rd(opt):
        s = rd(opt).replace("self.closeBtn = _MakeButton", "y = self._MikoInit(y)\n        self.closeBtn = _MakeButton", 1)
        s = re.sub(r"self\.SetSize\(([^,]+),\s*(\d+)\)", lambda m: f"self.SetSize({m.group(1)}, {int(m.group(2))+125})", s, count=1)
        s += """
    # MIKO_OPT_V1
    def _MikoInit(self, y):
        c = uimobilehud.LoadGfxConfig(); pn = {0:"Dusuk",1:"Orta",2:"Ultra"}
        self._mF = _MakeButton(self, "FPS: %d" % c["fps"], 0, y, self.OnMikoFps); y += 30
        self._mG = _MakeButton(self, "Grafik: %s" % pn.get(c["gfx"],"Ultra"), 0, y, self.OnMikoGfx); y += 30
        self._mS = _MakeButton(self, "Pazar Ismi: %s" % ("Acik" if c["shop_names"] else "Kapali"), 0, y, self.OnMikoShop); y += 30
        self._mH = _MakeButton(self, "HUD Boyut: %%%d" % c["hud_scale"], 0, y, self.OnMikoHud); y += 30
        return y
    def OnMikoFps(self):
        c = uimobilehud.LoadGfxConfig(); o = [30,60,120]; c["fps"] = o[(o.index(c["fps"])+1)%3] if c["fps"] in o else 60
        uimobilehud.SaveGfxConfig(c); self._mF.SetText("FPS: %d" % c["fps"])
    def OnMikoGfx(self):
        c = uimobilehud.LoadGfxConfig(); c["gfx"] = (c["gfx"]+1)%3; uimobilehud.SaveGfxConfig(c)
        self._mG.SetText("Grafik: %s" % {0:"Dusuk",1:"Orta",2:"Ultra"}[c["gfx"]])
    def OnMikoShop(self):
        c = uimobilehud.LoadGfxConfig(); c["shop_names"] = 0 if c["shop_names"] else 1; uimobilehud.SaveGfxConfig(c)
        self._mS.SetText("Pazar Ismi: %s" % ("Acik" if c["shop_names"] else "Kapali"))
    def OnMikoHud(self):
        c = uimobilehud.LoadGfxConfig(); o = [80,90,100,115,130]; c["hud_scale"] = o[(o.index(c["hud_scale"])+1)%5] if c["hud_scale"] in o else 100
        uimobilehud.SaveGfxConfig(c); self._mH.SetText("HUD Boyut: %%%d" % c["hud_scale"])
        try: d = uimobilehud.LoadDisplayConfig(); d["ui_scale"] = c["hud_scale"]/100.0; uimobilehud.SaveDisplayConfig(d)
        except Exception: pass
"""
        wr(opt, s)

def patch_java():
    b = os.path.join(ROOT, "android/app/src/main/java/com/metin2/client")
    jv = os.path.join(b, "JoystickView.java")
    if os.path.isfile(jv) and "MIKO_JOY_V1" not in rd(jv):
        wr(jv, "// MIKO_JOY_V1\n" + re.sub(r"Color\.argb\(\s*\d+\s*,\s*255\s*,\s*255\s*,\s*255\s*\)", "Color.argb(175, 196, 178, 140)", rd(jv)))
    gv = os.path.join(b, "GameView.java")
    if os.path.isfile(gv) and "MIKO_TOUCH_V1" not in rd(gv):
        old = "return x >= mJoystick.getLeft() && x < mJoystick.getRight() && y >= mJoystick.getTop() && y < mJoystick.getBottom();"
        new = "float cx=(mJoystick.getLeft()+mJoystick.getRight())*0.5f,cy=(mJoystick.getTop()+mJoystick.getBottom())*0.5f,r=Math.min(mJoystick.getWidth(),mJoystick.getHeight())*0.48f,dx=x-cx,dy=y-cy;return (dx*dx+dy*dy)<=(r*r);"
        wr(gv, "// MIKO_TOUCH_V1\n" + rd(gv).replace(old, new, 1))
    ma = os.path.join(b, "MainActivity.java")
    if os.path.isfile(ma) and "MIKO_120HZ_V1" not in rd(ma) and "setContentView(" in rd(ma):
        hk = '/* MIKO_120HZ_V1 */ try{android.view.WindowManager.LayoutParams lp=getWindow().getAttributes();lp.preferredRefreshRate=120.0f;getWindow().setAttributes(lp);}catch(Throwable ignored){}\n        setContentView('
        wr(ma, rd(ma).replace("setContentView(", hk, 1))

if __name__ == "__main__":
    patch_cpp_core(); patch_hud_and_options(); patch_java()
