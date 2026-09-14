"""Generate dependency-free PNG app icons during GitHub Pages deployment."""
import struct
import zlib
from pathlib import Path

BG = (124, 77, 104)
CREAM = (248, 245, 247)
HEART = (167, 111, 142)
WHITE = (255, 255, 255)

def crc(tag, data):
    return struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)

def chunk(tag, data):
    return struct.pack(">I", len(data)) + tag + data + crc(tag, data)

def segment_distance(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px-ax)*dx + (py-ay)*dy)/(dx*dx + dy*dy)))
    x, y = ax + t*dx, ay + t*dy
    return ((px-x)**2 + (py-y)**2) ** 0.5

def color_at(x, y):
    # Work in normalized coordinates so every icon size has identical artwork.
    dx, dy = x - .5, y - .5
    color = CREAM if dx*dx + dy*dy <= .318*.318 else BG

    hx = (x - .5) / .17
    hy = -(y - .53) / .17
    if (hx*hx + hy*hy - 1)**3 - hx*hx*hy**3 <= 0:
        color = HEART

    width = .020
    if (segment_distance(x,y,.425,.515,.485,.575) < width or
        segment_distance(x,y,.485,.575,.605,.425) < width):
        color = WHITE
    return color

def make_icon(size, filename):
    # Four samples per pixel produce clean edges without third-party libraries.
    offsets = (.25, .75)
    rows = []
    for py in range(size):
        row = bytearray([0])
        for px in range(size):
            samples = [color_at((px+ox)/size, (py+oy)/size)
                       for oy in offsets for ox in offsets]
            row.extend(sum(c[i] for c in samples)//4 for i in range(3))
            row.append(255)
        rows.append(row)
    raw = b"".join(rows)
    header = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    Path(filename).write_bytes(png)

for size in (180, 192, 512):
    make_icon(size, f"icon-{size}.png")
