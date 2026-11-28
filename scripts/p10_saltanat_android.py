#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re, sys

def clean_stage():
    for base in ("/tmp/m2stage", "android/assets", "client-src"):
        if not os.path.isdir(base):
            continue
        for root, _, files in os.walk(base):
            for fn in files:
                if not fn.lower().endswith(".py"):
                    continue
                p = os.path.join(root, fn)
                raw = open(p, "rb").read()
                if raw.startswith(b"\xef\xbb\xbf"):
                    raw = raw[3:]
                txt = raw.decode("utf-8", errors="ignore").replace("\r\n", "\n")
                txt = re.sub(r"[^\x09\x0a\x20-\x7e\u0080-\uffff]", "", txt)
                open(p, "wb").write(txt.encode("utf-8"))
    print("[p10] Temizlendi.")

def run(stage_only=False):
    clean_stage()

if __name__ == "__main__":
    run("--stage-only" in sys.argv)
    
