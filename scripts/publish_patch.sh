#!/usr/bin/env bash
set -euo pipefail
R="${GITHUB_WORKSPACE:-$(pwd)}/self-repo"
[ -d "$R" ] && cd "$R" || true
mkdir -p patch/files /tmp/m2bundle
git rm -f --ignore-unmatch patch/mobile2.keystore >/dev/null 2>&1 || true
rm -f patch/mobile2.keystore
[ -f /tmp/m2stage/metin2.cfg ] && cp /tmp/m2stage/metin2.cfg /tmp/m2bundle/metin2.cfg || true
[ -f patch/servers.json ] || printf '{"version":1,"servers":[{"name":"Offline","embedded":true}]}\n' > patch/servers.json
cp patch/servers.json /tmp/m2bundle/servers.json
rm -rf /tmp/m2pkg && mkdir -p /tmp/m2pkg
[ -f /tmp/m2bundle/metin2.cfg ] && cp /tmp/m2bundle/metin2.cfg /tmp/m2pkg/metin2.cfg || true
cp /tmp/m2bundle/servers.json /tmp/m2pkg/servers.json
cp -r patch/files/. /tmp/m2pkg/ 2>/dev/null || true
rm -f /tmp/m2bundle/m2patch.zip
(cd /tmp/m2pkg && zip -qr /tmp/m2bundle/m2patch.zip .)
V=""
if [ -f patch/manifest.txt ]; then V=$(head -n 1 patch/manifest.txt | tr -dc '0-9' || true); fi
P=$(( ${V:-1000} + 1 ))
T="patch-v$P"
if gh release view -R zenfasulyesi55-afk/Metin2-Lab-Releases "$T" >/dev/null 2>&1; then gh release upload -R zenfasulyesi55-afk/Metin2-Lab-Releases "$T" /tmp/m2bundle/m2patch.zip --clobber; else gh release create -R zenfasulyesi55-afk/Metin2-Lab-Releases "$T" /tmp/m2bundle/m2patch.zip --title "Yama v$P" --notes "Otomatik yama"; fi
printf "%s\nhttps://github.com/%s/releases/download/%s/m2patch.zip\n\n" "$P" "zenfasulyesi55-afk/Metin2-Lab-Releases" "$T" > patch/manifest.txt
git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"
git add patch/manifest.txt patch/servers.json
if ! git diff --cached --quiet; then git commit -m "chore: auto-publish patch v$P"; git pull --rebase origin main || true; git push origin HEAD:main; fi
