#!/usr/bin/env python3
ma_path = "client-src/r10dev.net OPENGL-ITJA/android/app/src/main/java/com/metin2/client/MainActivity.java"
ma = open(ma_path, "r", encoding="utf-8").read()
ma = ma.replace("mStatus.setText", "if (mStatus != null) mStatus.setText")
ma = ma.replace("mProgress.set", "if (mProgress != null) mProgress.set")
ma = ma.replace("mAction.set", "if (mAction != null) mAction.set")
ma = ma.replace("GameView view = activity.mView;", "GameView view = activity.mView; if (view == null) return;")
target = "ServerCatalog.refresh(getApplicationContext());"
p = []
p.append('setStatus("Checking patches...");')
p.append("DataInstaller.syncPatches(mDataDir, new DataInstaller.Progress() {")
p.append("public void onProgress(final long done, final long total) {")
p.append('setStatus("Downloading patch... " + (done >> 10) + " KB");')
p.append("}")
p.append("});")
p.append(target)
ma = ma.replace(target, "\n".join(p), 1) if ("DataInstaller.syncPatches" not in ma and target in ma) else ma
open(ma_path, "w", encoding="utf-8").write(ma)
di_path = "client-src/r10dev.net OPENGL-ITJA/android/app/src/main/java/com/metin2/client/DataInstaller.java"
ds = open(di_path, "r", encoding="utf-8").read()
ps = ds.find("static boolean isInstalled(File dataDir)")
pe = ds.find("private static void extract(")
assert ps != -1 and pe != -1, "DataInstaller.java metotlari bulunamadi!"
d = []
d.append("private static int sRemoteVer = -1;")
d.append('private static String sPatchUrl = "";')
d.append('private static String sBaseUrl = "";')
d.append("private static HttpURLConnection openFollowingRedirects(String urlStr, int cMs, int rMs) throws IOException {")
d.append("String current = urlStr;")
d.append("for (int hops = 0; hops < 5; ++hops) {")
d.append("HttpURLConnection conn = (HttpURLConnection) new URL(current).openConnection();")
d.append("conn.setInstanceFollowRedirects(false);")
d.append("conn.setConnectTimeout(cMs);")
d.append("conn.setReadTimeout(rMs);")
d.append("int code = conn.getResponseCode();")
d.append("if (code == 301 || code == 302 || code == 303 || code == 307 || code == 308) {")
d.append('String loc = conn.getHeaderField("Location");')
d.append("conn.disconnect();")
d.append('if (loc == null || loc.trim().isEmpty()) throw new IOException("Empty redirect");')
d.append("current = new URL(new URL(current), loc.trim()).toString();")
d.append("continue;")
d.append("}")
d.append("return conn;")
d.append("}")
d.append('throw new IOException("Too many redirects");')
d.append("}")
d.append("private static void fetchManifest() {")
d.append("if (BuildConfig.M2_DATA_URL.isEmpty()) return;")
d.append("HttpURLConnection conn = null;")
d.append("try {")
d.append("conn = openFollowingRedirects(BuildConfig.M2_DATA_URL, 5000, 5000);")
d.append("if (conn.getResponseCode() == HttpURLConnection.HTTP_OK) {")
d.append("java.io.BufferedReader r = new java.io.BufferedReader(new java.io.InputStreamReader(conn.getInputStream()));")
d.append("String l1 = r.readLine(), l2 = r.readLine(), l3 = r.readLine();")
d.append("r.close();")
d.append("if (l1 != null && !l1.trim().isEmpty()) sRemoteVer = Integer.parseInt(l1.trim());")
d.append("if (l2 != null) sPatchUrl = l2.trim();")
d.append("if (l3 != null) sBaseUrl = l3.trim();")
d.append("}")
d.append("} catch (Exception ignored) {")
d.append("} finally {")
d.append("if (conn != null) conn.disconnect();")
d.append("}")
d.append("}")
d.append("static boolean isInstalled(File dataDir) {")
d.append("if (!BuildConfig.M2_DATA_BUNDLED && BuildConfig.M2_DATA_URL.isEmpty()) return true;")
d.append('return new File(dataDir, "metin2.cfg").exists() && new File(dataDir, "server").exists();')
d.append("}")
d.append("static int installedVersion(File dataDir) {")
d.append("File f = new File(dataDir, VERSION_FILE);")
d.append("if (!f.exists()) return 0;")
d.append("try {")
d.append("InputStream in = new java.io.FileInputStream(f);")
d.append("byte[] buf = new byte[16];")
d.append("int n = in.read(buf);")
d.append("in.close();")
d.append("return n > 0 ? Integer.parseInt(new String(buf, 0, n).trim()) : 0;")
d.append("} catch (Exception e) { return 0; }")
d.append("}")
d.append("static void syncPatches(File dataDir, Progress progress) {")
d.append("try {")
d.append("fetchManifest();")
d.append("if (sRemoteVer > installedVersion(dataDir) && !sPatchUrl.isEmpty()) {")
d.append("dl(sPatchUrl, dataDir, progress);")
d.append("writeVersion(dataDir, sRemoteVer);")
d.append("}")
d.append("} catch (Exception e) {")
d.append('android.util.Log.w("Metin2Mobile", "patch sync skipped: " + e.getMessage());')
d.append("}")
d.append("}")
d.append("static void install(android.content.Context ctx, File dataDir, Progress progress) throws IOException {")
d.append("fetchManifest();")
d.append('boolean hasBase = new File(dataDir, "metin2.cfg").exists() && new File(dataDir, "server").exists();')
d.append("if (!hasBase) {")
d.append("if (!extractAssetZip(ctx, dataDir)) {")
d.append("if (!sBaseUrl.isEmpty()) dl(sBaseUrl, dataDir, progress);")
d.append('else throw new IOException("Temel oyun verisi eksik: Android/data/com.metin2.client.offline/files");')
d.append("}")
d.append("}")
d.append('if (!sPatchUrl.isEmpty()) { try { dl(sPatchUrl, dataDir, progress); } catch (Exception e) { android.util.Log.w("Metin2Mobile", "patch skip: " + e.getMessage()); } }')
d.append("writeVersion(dataDir, sRemoteVer > 0 ? sRemoteVer : BuildConfig.M2_DATA_VERSION);")
d.append("}")
d.append('private static boolean extractAssetZip(android.content.Context ctx, File dataDir) throws IOException {')
d.append('if (ctx == null) return false;')
d.append('dataDir.mkdirs();')
d.append('java.io.InputStream is;')
d.append('try { is = ctx.getAssets().open("m2base.zip"); } catch (IOException e) { return false; }')
d.append('try (java.util.zip.ZipInputStream zis = new java.util.zip.ZipInputStream(new java.io.BufferedInputStream(is, 65536))) {')
d.append('byte[] buf = new byte[65536]; java.util.zip.ZipEntry ze;')
d.append('String bc = dataDir.getCanonicalPath() + File.separator;')
d.append('while ((ze = zis.getNextEntry()) != null) {')
d.append('String n = ze.getName(); if (n == null || n.isEmpty() || n.equals("./") || n.equals(".")) { zis.closeEntry(); continue; }')
d.append('File out = new File(dataDir, n); String oc = out.getCanonicalPath();')
d.append('if (!oc.startsWith(bc) && !oc.equals(dataDir.getCanonicalPath())) { zis.closeEntry(); continue; }')
d.append('if (ze.isDirectory()) { out.mkdirs(); } else { File pr = out.getParentFile(); if (pr != null) pr.mkdirs(); try (java.io.FileOutputStream fos = new java.io.FileOutputStream(out)) { int r; while ((r = zis.read(buf)) > 0) fos.write(buf, 0, r); } }')
d.append('zis.closeEntry(); } }')
d.append('return new File(dataDir, "metin2.cfg").exists() && new File(dataDir, "server").exists(); }')
d.append("private static void writeVersion(File dataDir, int ver) throws IOException {")
d.append("OutputStream os = new FileOutputStream(new File(dataDir, VERSION_FILE));")
d.append("os.write(String.valueOf(ver).getBytes());")
d.append("os.close();")
d.append("}")
d.append("private static void dl(String urlStr, File dataDir, Progress progress) throws IOException {")
d.append("HttpURLConnection conn = openFollowingRedirects(urlStr, 15000, 60000);")
d.append("try {")
d.append('if (conn.getResponseCode() != HttpURLConnection.HTTP_OK) throw new IOException("HTTP " + conn.getResponseCode());')
d.append("long total = Build.VERSION.SDK_INT >= Build.VERSION_CODES.N ? conn.getContentLengthLong() : conn.getContentLength();")
d.append("extract(conn.getInputStream(), total, dataDir, progress);")
d.append("} finally { conn.disconnect(); }")
d.append("}")
d.append("")
ds_tail = ds[pe:]
ov = []
ov.append(" " * 8 + "OutputStream os = new FileOutputStream(new File(dataDir, VERSION_FILE));")
ov.append(" " * 8 + "os.write(String.valueOf(BuildConfig.M2_DATA_VERSION).getBytes());")
ov.append(" " * 8 + "os.close();")
ds_tail = ds_tail.replace("\n".join(ov), "// Version written after downloads")
open(di_path, "w", encoding="utf-8").write(ds[:ps] + "\n".join(d) + ds_tail)
print("OK: p2_client tamamlandi.")


# M2_MIKO_RAINBOW_NICK: Sadece [OK]Miko karakterinin nickini canli yanar doner yap
import os as _os, re as _re
_tt_cpp = None
_gt_hdr = None
for _r, _d, _fs in _os.walk("client-src"):
    for _fn in _fs:
        _fl = _fn.lower()
        if _fl == "pythontexttail.cpp":
            _tt_cpp = _os.path.join(_r, _fn)
        elif _fl == "grptextinstance.h":
            _gt_hdr = _os.path.join(_r, _fn)

if _tt_cpp and _gt_hdr:
    _tts = open(_tt_cpp, "r", encoding="utf-8", errors="ignore").read()
    _gts = open(_gt_hdr, "r", encoding="utf-8", errors="ignore").read()
    _getter = None
    if "GetValueStringReference" in _gts:
        _getter = "_m2ti->GetValueStringReference().c_str()"
    elif _re.search(r"\bGetValue\s*\(\s*\)", _gts):
        _getter = "_m2ti->GetValue()"
    _has_sc = bool(_re.search(r"SetColor\s*\(\s*float", _gts))
    _has_up = bool(_re.search(r"\bUpdate\s*\(\s*\)", _gts))
    if _getter and _has_sc and _has_up and "M2_MIKO_RAINBOW_NICK" not in _tts:
        _hdr_add = '\n#include <chrono>\n#include <cmath>\n#include <cstring>\n// M2_MIKO_RAINBOW_NICK\n'
        _m_pch = _re.search(r'#include\s+"[Ss]td[Aa]fx\.h"', _tts)
        if _m_pch:
            _tts = _tts[:_m_pch.end()] + _hdr_add + _tts[_m_pch.end():]
        else:
            _tts = _hdr_add + _tts
        _pat = _re.compile(r'([A-Za-z_][A-Za-z0-9_]*)\s*->\s*pTextInstance\s*->\s*Render\s*\(\s*\)\s*;')
        def _rep_miko(m):
            v = m.group(1)
            return (
                '{ auto* _m2ti = ' + v + '->pTextInstance; '
                'if (_m2ti && std::strstr(' + _getter + ', "[OK]Miko")) { '
                'static auto _m2t0 = std::chrono::steady_clock::now(); '
                'double _m2s = std::chrono::duration<double>(std::chrono::steady_clock::now() - _m2t0).count() * 4.5; '
                'float _m2r = 0.55f + 0.45f * std::sin((float)_m2s); '
                'float _m2g = 0.55f + 0.45f * std::sin((float)_m2s + 2.094395f); '
                'float _m2b = 0.55f + 0.45f * std::sin((float)_m2s + 4.188790f); '
                '_m2ti->SetColor(_m2r, _m2g, _m2b); _m2ti->Update(); } } ' + m.group(0)
            )
        _tts_new, _cnt = _pat.subn(_rep_miko, _tts)
        if _cnt > 0:
            open(_tt_cpp, "w", encoding="utf-8").write(_tts_new)
            print("OK: [OK]Miko yanar doner nick istemciye islendi (" + str(_cnt) + " nokta).")
        else:
            print("WARN: PythonTextTail Render deseni bulunamadi, atlandi.")
    else:
        print("WARN: GrpTextInstance metotlari eslesmedi, derleme guvenligi icin atlandi.")
else:
    print("WARN: PythonTextTail.cpp veya GrpTextInstance.h bulunamadi.")
