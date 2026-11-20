#!/usr/bin/env bash
set -euo pipefail
cd self-repo && mkdir -p patch
git rm -f --ignore-unmatch patch/mobile2.keystore >/dev/null 2>&1 || true && rm -f patch/mobile2.keystore
PVER=$((1000 + GITHUB_RUN_NUMBER)) && TAG="patch-v$PVER"
if gh release view "$TAG" >/dev/null 2>&1; then gh release upload "$TAG" /tmp/m2bundle/m2patch.zip --clobber; else gh release create "$TAG" /tmp/m2bundle/m2patch.zip --title "Acik Kaynak Yama v$PVER" --notes "Temiz istemci yapilandirma yamasi"; fi
printf "%s\nhttps://github.com/%s/releases/download/%s/m2patch.zip\n\n" "$PVER" "$GITHUB_REPOSITORY" "$TAG" > patch/manifest.txt
[ ! -f patch/servers.json ] && printf '{"version":1,"servers":[{"name":"Offline","embedded":true}]}\n' > patch/servers.json
git config user.name "github-actions[bot]" && git config user.email "github-actions[bot]@users.noreply.github.com"
git add patch/manifest.txt patch/servers.json
if ! git diff --cached --quiet; then git commit -m "chore: publish config patch v$PVER" && (git pull --rebase || true) && git push; fi
