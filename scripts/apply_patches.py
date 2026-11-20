#!/usr/bin/env python3
import os, subprocess, sys

d = os.path.dirname(os.path.abspath(__file__))
for name in ("p1_server.py", "p2_client.py", "p3_config.py"):
    subprocess.check_call([sys.executable, os.path.join(d, name)])
    