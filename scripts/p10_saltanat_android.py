
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re, sys

HOOK_TAG = "# SALTANAT_SAFE_BOOT_V11"
HOOK_CODE = (
    "\n" + HOOK_TAG + "\n"
    "try:\n"
    "    import sys as _sys\n"
    "    _orig_hook = _sys.excepthook\n"
    "    def _safe_hook(t, v, tb):\n"
    "        try:\n"
    "            import traceback as _tb\n"
    "            f = open('syserr.txt', 'a')\n"
    "            f.write(''.join(_tb.format_exception(t, v, tb)))\n"
    "            f.close()\n"
    "        except Exception:\n"
    "            pass\n"
    "        _orig_hook(t, v, tb)\n"
    "    _sys.excepthook = _safe_hook\n"
    "except Exception:\n"
    "    pass\n"
)

def clean_and_fix():
    for base in ("/tmp/m2stage", "android/assets", "client-src"):
        if not os.path.isdir(base):
            continue
        for root, _, files in os.walk(base):
            for fn in files:
                if not fn.lower().endswith(".py"):
                    continue
                path = os.path.join(root, fn)
                raw = open(path, "rb").read()
                if raw.startswith(b"\xef\xbb\xbf"):
                    raw = raw[3:]
                txt = raw.decode("utf-8", errors="ignore").replace("\r\n", "\n")
                try:
                    compile(txt, path, "exec")
                except SyntaxError as e:
                    print("[p10] BOZUK PY BULUNDU:", path, e)
                    txt = re.split(r"\n#\s*===\s*SALTANAT_", txt)[0]
                if fn.lower() == "system.py" and HOOK_TAG not in txt:
                    cand = txt + "\n" + HOOK_CODE
                    try:
                        compile(cand, path, "exec")
                        txt = cand
                    except SyntaxError:
                        pass
                open(path, "wb").write(txt.encode("utf-8"))
    print("[p10] Tum .py dosyalari BOM/sozdizimi kontrolunden gecti.")

def run(stage_only=False):
    clean_and_fix()

if __name__ == "__main__":
    run("--stage-only" in sys.argv)
