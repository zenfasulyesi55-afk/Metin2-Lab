#!/usr/bin/env bash
set -euo pipefail
KS_PATH="/tmp/mobile2.keystore"
KS_PASS="${KEYSTORE_PASS:-mobile2lab}"
KS_ALIAS="${KEY_ALIAS:-mobile2}"
K_PASS="${KEY_PASS:-$KS_PASS}"
if [ -n "${KEYSTORE_B64:-}" ]; then printf '%s' "$KEYSTORE_B64" | base64 -d > "$KS_PATH"; else keytool -genkeypair -noprompt -keystore "$KS_PATH" -storepass "$KS_PASS" -alias "$KS_ALIAS" -keypass "$K_PASS" -keyalg RSA -keysize 2048 -validity 10000 -dname "CN=MOBILE2-LAB,O=Mobile2,C=TR"; fi
