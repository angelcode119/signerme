#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import struct
import subprocess
import random
import string
import hashlib
import tempfile

APKSIGNER_PATH = r"C:\Users\awmeiiir\AppData\Local\Android\Sdk\build-tools\34.0.0\apksigner.bat"

def r():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))

def p():
    return ''.join(random.choice(string.ascii_letters + string.digits + "!@#$%^&*") for _ in range(16))

def k():
    ks = os.path.join(tempfile.gettempdir(), f"t_{hashlib.md5(str(random.getrandbits(128)).encode()).hexdigest()[:8]}.keystore")
    pw = p()
    al = "a_" + r()
    if not os.path.exists(ks):
        subprocess.run([
            "keytool", "-genkey", "-v",
            "-keystore", ks, "-alias", al,
            "-keyalg", "RSA", "-keysize", "2048", "-validity", "10000",
            "-storepass", pw, "-keypass", pw,
            "-dname", "CN=Unknown"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return ks, pw, al

def m(i, o):
    with open(i, 'rb') as f: d = f.read()
    e = d.rfind(b'\x50\x4B\x05\x06')
    if e == -1: sys.exit(1)
    cs = struct.unpack_from('<I', d, e + 12)[0]
    co = struct.unpack_from('<I', d, e + 16)[0]
    p = co
    md = bytearray(d)
    while p < co + cs:
        if d[p:p+4] != b'\x50\x4B\x01\x02': break
        b = p + 8
        f = struct.unpack_from('<H', d, b)[0]
        if not (f & 0x0001):
            f |= 0x0001
            struct.pack_into('<H', md, b, f)
        nl = struct.unpack_from('<H', d, p + 28)[0]
        el = struct.unpack_from('<H', d, p + 30)[0]
        p += 46 + nl + el
    with open(o, 'wb') as f: f.write(md)
    return o

def s(a, ks, pw, al):
    o = a.replace(".apk", "_s.apk")
    subprocess.run([
        APKSIGNER_PATH, "sign",
        "--ks", ks, "--ks-pass", f"pass:{pw}",
        "--ks-key-alias", al, "--out", o, a
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return o

def main():
    if len(sys.argv) != 2: sys.exit(1)
    inp = sys.argv[1]
    if not os.path.exists(inp): sys.exit(1)

    base = os.path.splitext(os.path.basename(inp))[0]
    temp = f"{base}_1.apk"
    out = f"{base}_out.apk"

    # 1. تغییر Bit Flag (بدون باز کردن فایل‌ها)
    m(inp, temp)

    # 2. امضا
    ks, pw, al = k()
    final = s(temp, ks, pw, al)

    # پاکسازی
    if os.path.exists(temp): os.remove(temp)

    # خروجی نهایی
    if final != out:
        os.replace(final, out)

    print(f"Done: {out}")

if __name__ == "__main__":
    main()