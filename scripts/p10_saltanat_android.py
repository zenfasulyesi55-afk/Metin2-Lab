#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

def run(stage_only=False):
    print("[p10] Guvenli pasif mod (stage_only=%s)" % stage_only)

if __name__ == "__main__":
    run("--stage-only" in sys.argv)
    
