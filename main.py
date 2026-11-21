# main.py — news-image-20261121 entry (Python 3.13, standard library only).
#
# The entry is the newspaper front page "THE WORLD IN ONE DAY — Saturday
# 21 November 2026" held in this repository as entry.png (1024x1024,
# 38 verified stories from six continents, 8 illustrated panels, a world
# map with 12 numbered pins, a day-in-figures strip). This program copies
# it to /output/entry.png. It is deterministic: the same bytes are written
# on every run.
#
# Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
#   mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import hashlib
import os
import shutil
import struct

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"
MAX_BYTES = 1 << 20  # at most 1 MiB
MAX_SIDE = 1024  # at most 1024 by 1024 pixels


def jpeg_size(data):
    """Width and height from the first SOF marker of a JPEG byte string."""
    pos = 2  # skip SOI
    while pos + 9 <= len(data):
        if data[pos] != 0xFF:
            raise AssertionError("malformed JPEG marker")
        marker = data[pos + 1]
        if marker in (0xD8, 0xD9, 0x01) or 0xD0 <= marker <= 0xD7:
            pos += 2
            continue
        seg = struct.unpack(">H", data[pos + 2:pos + 4])[0]
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                      0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            height, width = struct.unpack(">HH", data[pos + 5:pos + 9])
            return width, height
        pos += 2 + seg
    raise AssertionError("no SOF marker in JPEG")


def check_source(path):
    """Refuse anything that is not a PNG/JPEG inside the gate's limits."""
    size = os.path.getsize(path)
    if size > MAX_BYTES:
        raise AssertionError("source too large: %d bytes > 1 MiB" % size)
    with open(path, "rb") as handle:
        head = handle.read(65536)
    if head[:8] == PNG_MAGIC:
        if head[12:16] != b"IHDR":
            raise AssertionError("source has no IHDR chunk")
        width, height = struct.unpack(">II", head[16:24])
    elif head[:3] == JPEG_MAGIC:
        width, height = jpeg_size(head)
    else:
        raise AssertionError("source is neither PNG nor JPEG")
    if width > MAX_SIDE or height > MAX_SIDE:
        raise AssertionError("source too large: %dx%d > 1024x1024"
                             % (width, height))
    return size, width, height


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_head(path, count=8):
    with open(path, "rb") as handle:
        return handle.read(count)


here = os.path.dirname(os.path.abspath(__file__))
out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
os.makedirs(out_dir, exist_ok=True)
src = os.path.join(here, "entry.png")
dst = os.path.join(out_dir, "entry.png")
if os.path.abspath(dst) == os.path.abspath(src):
    raise AssertionError("output path is the source file itself")
size, width, height = check_source(src)
shutil.copyfile(src, dst)
# The copy must be exact: same size, same SHA-256, same leading bytes.
if os.path.getsize(dst) != os.path.getsize(src):
    raise AssertionError("copy incomplete")
if sha256_file(dst) != sha256_file(src):
    raise AssertionError("copy corrupted")
if file_head(dst) != file_head(src):
    raise AssertionError("copy header mismatch")
print("wrote %s (%d bytes, %dx%d, sha256 %s...)"
      % (dst, os.path.getsize(dst), width, height, sha256_file(dst)[:16]))
