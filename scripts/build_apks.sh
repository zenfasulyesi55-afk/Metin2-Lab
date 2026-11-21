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
(cd "$CLIENT_ANDROID" && M2_SERVER_SRC=/tmp/m2dev-server-src /tmp/gd/gradle-8.13/bin/gradle assembleDebug --no-daemon --console=plain -Pm2profile=offline -Pm2abi=arm64-v8a && cp app/build/outputs/apk/debug/app-debug.apk /tmp/m2bundle/metin2-live-base.apk)
python3 -c 'import zipfile; n=set(zipfile.ZipFile("/tmp/m2bundle/metin2-live-base.apk").namelist()); req=["lib/arm64-v8a/libmetin2_mobile.so","lib/arm64-v8a/libm2game.so","lib/arm64-v8a/libm2db.so"]; miss=[x for x in req if x not in n]; assert not miss, f"Eksik native kutuphaneler: {miss}"; print("OK: ARM64 native kutuphaneler dogrulandi.")'
(cd "$GM_DIR" && /tmp/gd/gradle-8.13/bin/gradle assembleDebug --no-daemon --console=plain && cp app/build/outputs/apk/debug/app-debug.apk /tmp/m2bundle/metin2-gm-panel.apk)
ls -lh /tmp/m2bundle/metin2-live-base.apk /tmp/m2bundle/metin2-gm-panel.apk
