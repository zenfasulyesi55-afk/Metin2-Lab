#!/usr/bin/env python3
import os, zipfile
REPO_SLUG = os.environ.get("GITHUB_REPOSITORY", "zenfasulyesi55-afk/Metin2-Lab")
sr = "client-src/r10dev.net OPENGL-ITJA/clientsource"
fps = [os.path.join(r, fn) for r, _, fs in os.walk(sr) for fn in fs if fn.endswith((".cpp", ".c", ".h"))]
cfg = ["WIDTH\t1280", "HEIGHT\t720", "BPP\t32", "FREQUENCY\t60", "SOFTWARE_CURSOR\t0", "OBJECT_CULLING\t1", "VISIBILITY\t3", "MUSIC_VOLUME\t0.5", "VOICE_VOLUME\t5", "GAMMA\t3", "IS_SAVE_ID\t1", "SAVE_ID\ttest", "PRE_LOADING_DELAY_TIME\t20", "DECOMPRESSED_TEXTURE\t1", "TEXTURE_LEVEL\t0", "SHADOW_LEVEL\t0", "EFFECT_LEVEL\t0"]
mcfg="/tmp/m2stage/metin2.cfg"
base_cfg=open(mcfg,"r",encoding="utf-8",errors="ignore").read().splitlines() if os.path.exists(mcfg) else cfg
kv={ps[0]:ps[1] for x in base_cfg for ps in [x.strip().split(None,1)] if len(ps)==2}
kv.update({"DECOMPRESSED_TEXTURE":"1","SHADOW_LEVEL":"0","IS_SAVE_ID":"1","SAVE_ID":"test"})
open(mcfg,"w",encoding="utf-8").write("\n".join(k+"\t"+v for k,v in kv.items())+"\n")
prof_path = "client-src/r10dev.net OPENGL-ITJA/android/profiles/offline.properties"
pr = []
pr.append("m2.abi=arm64-v8a")
pr.append("m2.serverMode=embedded")
pr.append("m2.serverHost=127.0.0.1")
pr.append("m2.authPort=11000")
pr.append("m2.channelPort=11011")
pr.append("m2.dataUrl=https://raw.githubusercontent.com/" + REPO_SLUG + "/main/patch/manifest.txt")
pr.append("m2.serverListUrl=https://raw.githubusercontent.com/" + REPO_SLUG + "/main/patch/servers.json")
pr.append("m2.dataVersion=1")
pr.append("m2.versionName=live")
pr.append("m2.applicationIdSuffix=.offline")
pr.append("m2.appLabel=Metin2")
open(prof_path, "w", encoding="utf-8").write("\n".join(pr) + "\n")
bg_path = "client-src/r10dev.net OPENGL-ITJA/android/app/build.gradle"
bgs = open(bg_path, "r", encoding="utf-8").read()
sg = []
sg.append(" " * 4 + "signingConfigs {")
sg.append(" " * 8 + "debug {")
sg.append(" " * 12 + 'storeFile file("/tmp/mobile2.keystore")')
sg.append(" " * 12 + 'storePassword System.getenv("KEYSTORE_PASS") ?: "mobile2lab"')
sg.append(" " * 12 + 'keyAlias System.getenv("KEY_ALIAS") ?: "mobile2"')
sg.append(" " * 12 + 'keyPassword System.getenv("KEY_PASS") ?: System.getenv("KEYSTORE_PASS") ?: "mobile2lab"')
sg.append(" " * 8 + "}")
sg.append(" " * 4 + "}")
sg.append("")
sg.append(" " * 4 + "buildTypes {")
bgs = bgs.replace(" " * 4 + "buildTypes {", "\n".join(sg), 1) if "signingConfigs" not in bgs else bgs
old_dbg = " " * 8 + "debug {\n" + " " * 12 + "debuggable true"
new_dbg = " " * 8 + "debug {\n" + " " * 12 + "signingConfig signingConfigs.debug\n" + " " * 12 + "debuggable true"
bgs = bgs.replace(old_dbg, new_dbg, 1) if "signingConfig signingConfigs.debug" not in bgs else bgs
open(bg_path, "w", encoding="utf-8").write(bgs)
os.makedirs("/tmp/m2bundle", exist_ok=True)
zf = zipfile.ZipFile("/tmp/m2bundle/m2patch.zip", "w", zipfile.ZIP_DEFLATED)
zf.write("/tmp/m2stage/metin2.cfg", "metin2.cfg")
zf.close()
print("OK: p3_config tamamlandi.")
