import os, shutil
base = "client-src/r10dev.net OPENGL-ITJA/android/app/src/main"
jdir = os.path.join(base, "java/com/metin2/client")
for f in ("GameApkProvider.java", "GameUpdaterUI.java"):
    shutil.copyfile(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), "game_extras"), f), os.path.join(jdir, f))
ma = os.path.join(jdir, "MainActivity.java")
s = open(ma).read()
if "GameUpdaterUI" not in s:
    open(ma, "w").write(s.replace("setContentView(layout);", "setContentView(GameUpdaterUI.wrap(this, layout, mStatus));", 1))
mf = os.path.join(base, "AndroidManifest.xml")
m = open(mf).read()
if "REQUEST_INSTALL_PACKAGES" not in m:
    m = m.replace("<application", '<uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES" />\n<application', 1)
if "GameApkProvider" not in m:
    m = m.replace("</application>", '<provider android:name=".GameApkProvider" android:authorities="${applicationId}.gameapkprovider" android:exported="false" android:grantUriPermissions="true" />\n</application>', 1)
open(mf, "w").write(m)
