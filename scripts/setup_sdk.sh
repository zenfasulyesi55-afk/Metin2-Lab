#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update -qq
sudo apt-get install -y -qq \
  libsodium23 liblzo2-2 rsync patch python3-pil \
    zip unzip curl ninja-build build-essential cmake imagemagick

    SDK_ROOT="${ANDROID_HOME:-/usr/local/lib/android/sdk}"
    SDKMGR=$(find "$SDK_ROOT" -name sdkmanager -type f | head -n 1)
    if [ -z "$SDKMGR" ]; then
      echo "HATA: sdkmanager bulunamadi ($SDK_ROOT)" >&2
        exit 1
        fi

        ((yes || true) | "$SDKMGR" --sdk_root="$SDK_ROOT" --licenses >/dev/null 2>&1 || true)

        "$SDKMGR" --sdk_root="$SDK_ROOT" \
          "platform-tools" \
            "platforms;android-33" \
              "platforms;android-35" \
                "build-tools;33.0.2" \
                  "build-tools;35.0.0" \
                    "ndk;25.2.9519653" \
                      "cmake;3.22.1"
                      