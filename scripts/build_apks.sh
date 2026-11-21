#!/usr/bin/env bash
set -euo pipefail
SDK_ROOT="${ANDROID_HOME:-/usr/local/lib/android/sdk}"
CLIENT_SRC="client-src/r10dev.net OPENGL-ITJA/clientsource"
CLIENT_ANDROID="client-src/r10dev.net OPENGL-ITJA/android"
GM_DIR="self-repo/gm-panel"
[ -d "$CLIENT_SRC/UserInterface" ] && [ ! -e "$CLIENT_SRC/userInterface" ] && ln -s UserInterface "$CLIENT_SRC/userInterface" || true
[ -d "$CLIENT_SRC/eterPack" ] && [ ! -e "$CLIENT_SRC/EterPack" ] && ln -s eterPack "$CLIENT_SRC/EterPack" || true
echo "sdk.dir=$SDK_ROOT" > "$CLIENT_ANDROID/local.properties"
echo "sdk.dir=$SDK_ROOT" > "$GM_DIR/local.properties"
if [ ! -x /tmp/gd/gradle-8.13/bin/gradle ]; then curl -sL https://services.gradle.org/distributions/gradle-8.13-bin.zip -o /tmp/g.zip && unzip -q -o /tmp/g.zip -d /tmp/gd && rm -f /tmp/g.zip; fi
mkdir -p /tmp/m2bundle
[ -f /tmp/m2stage/servers.json ] || ([ -f self-repo/patch/servers.json ] && cp self-repo/patch/servers.json /tmp/m2stage/servers.json || printf '{"version":1,"servers":[{"name":"Offline","embedded":true}]}\n' > /tmp/m2stage/servers.json)
mkdir -p "$CLIENT_ANDROID/app/src/main/assets"
BASE_ZIP="$(pwd)/$CLIENT_ANDROID/app/src/main/assets/m2base.zip"
rm -f "$BASE_ZIP"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p /tmp/m2stage/lib
for f in posixpath.py genericpath.py stat.py; do if [ ! -f "/tmp/m2stage/lib/$f" ]; then fp=$(find client-src -name "$f" -print -quit 2>/dev/null || true); if [ -n "$fp" ]; then cp "$fp" "/tmp/m2stage/lib/$f"; fi; fi; done
[ -f /tmp/m2stage/lib/posixpath.py ] || cp "$SCRIPT_DIR/posixpath_fallback.py" /tmp/m2stage/lib/posixpath.py
(cd /tmp/m2stage && zip -qr -1 "$BASE_ZIP" .)
(cd /tmp/m2serverpack && zip -qr -1 -u "$BASE_ZIP" .)
ls -lh "$BASE_ZIP"
(cd "$CLIENT_ANDROID" && GRADLE_OPTS="-Xmx4g" M2_SERVER_SRC=/tmp/m2dev-server-src /tmp/gd/gradle-8.13/bin/gradle assembleDebug --no-daemon --console=plain -Dorg.gradle.jvmargs="-Xmx4g -XX:MaxMetaspaceSize=1g" -Pm2profile=offline -Pm2abi=arm64-v8a && cp app/build/outputs/apk/debug/app-debug.apk /tmp/m2bundle/metin2-live-base.apk)
python3 -c 'import zipfile; n=set(zipfile.ZipFile("/tmp/m2bundle/metin2-live-base.apk").namelist()); req=["lib/arm64-v8a/libmetin2_mobile.so","lib/arm64-v8a/libm2game.so","lib/arm64-v8a/libm2db.so","assets/m2base.zip"]; miss=[x for x in req if x not in n]; assert not miss, f"Eksik dosyalar: {miss}"; print("OK: ARM64 native kutuphaneler ve m2base.zip dogrulandi.")'
(cd "$GM_DIR" && /tmp/gd/gradle-8.13/bin/gradle assembleDebug --no-daemon --console=plain && cp app/build/outputs/apk/debug/app-debug.apk /tmp/m2bundle/metin2-gm-panel.apk)
ls -lh /tmp/m2bundle/metin2-live-base.apk /tmp/m2bundle/metin2-gm-panel.apk
