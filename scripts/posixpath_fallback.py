import os, sys
curdir, pardir, extsep, sep, pathsep, defpath, altsep, devnull = ".", "..", ".", "/", ":", ":/bin:/usr/bin", None, "/dev/null"
supports_unicode_filenames = False
def normcase(s): return s
def isabs(s): return s.startswith("/")
def join(a, *p):
    path = a
    for b in p:
        if b.startswith("/"): path = b
        elif path == "" or path.endswith("/"): path += b
        else: path += "/" + b
    return path
def split(p):
    i = p.rfind("/") + 1
    head, tail = p[:i], p[i:]
    if head and head != "/" * len(head): head = head.rstrip("/")
    return head, tail
def splitdrive(p): return "", p
def splitext(p):
    s = p.rfind("/")
    d = p.rfind(".")
    if d > s:
        f = s + 1
        while f < d:
            if p[f] != ".": return p[:d], p[d:]
            f += 1
    return p, ""
def basename(p): return p[p.rfind("/") + 1:]
def dirname(p):
    h = p[:p.rfind("/") + 1]
    if h and h != "/" * len(h): h = h.rstrip("/")
    return h
def exists(p):
    try: os.stat(p); return True
    except OSError: return False
def lexists(p):
    try: os.lstat(p); return True
    except OSError: return False
def isdir(p):
    try: return (os.stat(p).st_mode & 0xf000) == 0x4000
    except OSError: return False
def isfile(p):
    try: return (os.stat(p).st_mode & 0xf000) == 0x8000
    except OSError: return False
def islink(p):
    try: return (os.lstat(p).st_mode & 0xf000) == 0xa000
    except (OSError, AttributeError): return False
def ismount(p): return False
def getsize(p): return os.stat(p).st_size
def getmtime(p): return os.stat(p).st_mtime
def getatime(p): return os.stat(p).st_atime
def getctime(p): return os.stat(p).st_ctime
def normpath(p):
    if p == "": return "."
    ini = p.startswith("/")
    if ini and p.startswith("//") and not p.startswith("///"): ini = 2
    out = []
    for c in p.split("/"):
        if c in ("", "."): continue
        if c != ".." or (not ini and not out) or (out and out[-1] == ".."): out.append(c)
        elif out: out.pop()
    p = "/".join(out)
    if ini: p = "/" * ini + p
    return p or "."
def abspath(p):
    if not isabs(p): p = join(os.getcwd(), p)
    return normpath(p)
def realpath(p): return abspath(p)
def expanduser(p): return p
def expandvars(p): return p
def commonprefix(m):
    if not m: return ""
    s1, s2 = min(m), max(m)
    for i, c in enumerate(s1):
        if c != s2[i]: return s1[:i]
    return s1
def relpath(p, start=curdir):
    if not p: raise ValueError("no path")
    sl = [x for x in abspath(start).split("/") if x]
    pl = [x for x in abspath(p).split("/") if x]
    i = len(commonprefix([sl, pl]))
    r = [".."] * (len(sl) - i) + pl[i:]
    return join(*r) if r else curdir
def samefile(f1, f2):
    s1, s2 = os.stat(f1), os.stat(f2)
    return s1.st_ino == s2.st_ino and s1.st_dev == s2.st_dev
def sameopenfile(f1, f2):
    s1, s2 = os.fstat(f1), os.fstat(f2)
    return s1.st_ino == s2.st_ino and s1.st_dev == s2.st_dev
