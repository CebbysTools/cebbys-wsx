import json
import struct
import zlib
from pathlib import Path

REFERENCES = Path(__file__).resolve().parent / "scenes.json"
GRID = (16, 9)


def load_bmp(path):
    data = Path(path).read_bytes()
    offset, = struct.unpack_from("<I", data, 10)
    width, height = struct.unpack_from("<ii", data, 18)
    bpp = struct.unpack_from("<H", data, 28)[0] // 8
    stride = (width * bpp + 3) & ~3
    bottom_up = height > 0
    height = abs(height)
    rows = []
    for row in range(height):
        source = height - 1 - row if bottom_up else row
        start = offset + source * stride
        rows.append([(data[start + x * bpp + 2], data[start + x * bpp + 1], data[start + x * bpp]) for x in range(width)])
    return width, height, rows


def signature(path):
    width, height, rows = load_bmp(path)
    cells = []
    for gy in range(GRID[1]):
        for gx in range(GRID[0]):
            total = count = 0
            for y in range(gy * height // GRID[1], (gy + 1) * height // GRID[1], 4):
                for x in range(gx * width // GRID[0], (gx + 1) * width // GRID[0], 4):
                    r, g, b = rows[y][x]
                    total += (r * 299 + g * 587 + b * 114) // 1000
                    count += 1
            cells.append(total // max(count, 1))
    return cells


def write_png(bmp_path, png_path, scale=2):
    width, height, rows = load_bmp(bmp_path)
    out_w, out_h = width // scale, height // scale
    raw = bytearray()
    for y in range(out_h):
        raw.append(0)
        for x in range(out_w):
            raw.extend(rows[y * scale][x * scale])
    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xffffffff)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", out_w, out_h, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(bytes(raw), 6)) + chunk(b"IEND", b"")
    Path(png_path).write_bytes(png)


def distance(a, b):
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)


def identify(cells, threshold=12.0):
    references = json.loads(REFERENCES.read_text()) if REFERENCES.exists() else {}
    best = min(((distance(cells, ref), name) for name, ref in references.items()), default=None)
    if best is None or best[0] > threshold:
        return "unknown", best[0] if best else None
    return best[1], round(best[0], 1)


def remember(name, cells):
    references = json.loads(REFERENCES.read_text()) if REFERENCES.exists() else {}
    references[name] = cells
    REFERENCES.write_text(json.dumps(references, indent=1))
