#!/usr/bin/env python3
import os, subprocess, sys

d = os.path.dirname(os.path.abspath(__file__))
for name in ("p1_server.py", "p2_client.py", "p3_config.py", "p4_server_overhaul.py", "p5_client_overhaul.py", "p6_game_ui_updater.py", "p7_mega_overhaul.py"):
    subprocess.check_call([sys.executable, os.path.join(d, name)])
    
import sys as _s, os as _o
_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import p8_v3_stage_overhaul as _p8; _p8.run()
