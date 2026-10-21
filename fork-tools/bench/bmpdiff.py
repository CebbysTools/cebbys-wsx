import struct
import sys


def load(path):
    data = open(path, "rb").read()
    offset, = struct.unpack_from("<I", data, 10)
    width, height = struct.unpack_from("<ii", data, 18)
    bits, = struct.unpack_from("<H", data, 28)
    return width, abs(height), bits // 8, data[offset:]


def main():
    a, b = load(sys.argv[1]), load(sys.argv[2])
    if a[:3] != b[:3]:
        print("size differs", a[:3], b[:3])
        return
    width, height, bpp, pa = a
    pb = b[3]
    stride = (width * bpp + 3) & ~3
    differing = 0
    total = 0
    worst = 0
    for row in range(height):
        start = row * stride
        for column in range(0, width * bpp, bpp):
            pixel_a = pa[start + column:start + column + 3]
            pixel_b = pb[start + column:start + column + 3]
            delta = max(abs(x - y) for x, y in zip(pixel_a, pixel_b))
            total += 1
            if delta > 8:
                differing += 1
            worst = max(worst, delta)
    print(f"{width}x{height}: {differing} of {total} pixels differ by more than 8 ({100.0 * differing / total:.3f}%), largest channel difference {worst}")


if __name__ == "__main__":
    main()
