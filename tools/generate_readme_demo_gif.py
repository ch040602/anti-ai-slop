from __future__ import annotations

import argparse
from pathlib import Path

WIDTH = 960
HEIGHT = 540
FRAME_COUNT = 20
DELAY_CS = 9

PALETTE = [
    (18, 24, 32),
    (31, 41, 55),
    (49, 64, 84),
    (236, 240, 244),
    (160, 174, 192),
    (58, 132, 255),
    (38, 196, 133),
    (255, 183, 77),
    (238, 92, 92),
    (116, 89, 255),
    (14, 165, 233),
    (22, 101, 52),
    (64, 77, 97),
    (245, 247, 250),
    (96, 165, 250),
    (15, 118, 110),
]


def fill_rect(pixels: bytearray, x: int, y: int, width: int, height: int, color: int) -> None:
    x2 = min(WIDTH, x + width)
    y2 = min(HEIGHT, y + height)
    for row in range(max(0, y), y2):
        start = row * WIDTH + max(0, x)
        pixels[start : row * WIDTH + x2] = bytes([color]) * (x2 - max(0, x))


def draw_frame(index: int) -> bytes:
    pixels = bytearray([0]) * (WIDTH * HEIGHT)

    fill_rect(pixels, 0, 0, WIDTH, HEIGHT, 0)
    fill_rect(pixels, 0, 0, WIDTH, 72, 1)
    fill_rect(pixels, 38, 28, 260, 14, 3)
    fill_rect(pixels, 38, 50, 410, 8, 4)

    fill_rect(pixels, 40, 100, 250, 380, 1)
    fill_rect(pixels, 320, 100, 600, 380, 1)
    fill_rect(pixels, 60, 126, 130, 12, 3)
    fill_rect(pixels, 340, 126, 190, 12, 3)

    steps = [
        ("inventory", 5),
        ("spec", 6),
        ("tasks", 7),
        ("validate", 10),
        ("review", 9),
    ]
    active = min(len(steps) - 1, index // 4)
    for pos, (_, color) in enumerate(steps):
        y = 166 + pos * 54
        step_color = color if pos <= active else 12
        fill_rect(pixels, 64, y, 180, 26, step_color)
        fill_rect(pixels, 78, y + 8, 90 + (pos * 16), 5, 3 if pos <= active else 4)
        if pos < len(steps) - 1:
            fill_rect(pixels, 150, y + 28, 8, 24, 2 if pos <= active else 12)

    fill_rect(pixels, 340, 162, 535, 56, 2)
    fill_rect(pixels, 360, 182, 170 + index * 11, 10, 5)
    fill_rect(pixels, 360, 200, 105, 6, 4)

    for card in range(4):
        y = 246 + card * 50
        color = [6, 7, 10, 9][card]
        fill_rect(pixels, 340, y, 535, 34, 2)
        fill_rect(pixels, 360, y + 10, 18, 14, color if card <= active else 12)
        fill_rect(pixels, 392, y + 11, 260 + card * 34, 5, 3)
        fill_rect(pixels, 392, y + 22, 120 + card * 20, 4, 4)

    progress = 80 + index * 36
    fill_rect(pixels, 340, 460, 535, 10, 12)
    fill_rect(pixels, 340, 460, min(535, progress), 10, 6)
    fill_rect(pixels, 840, 30, 44, 14, 6 if index == FRAME_COUNT - 1 else 7)

    return bytes(pixels)


def pack_lzw(indices: bytes, min_code_size: int) -> bytes:
    clear_code = 1 << min_code_size
    end_code = clear_code + 1
    dictionary = {(value,): value for value in range(clear_code)}
    next_code = end_code + 1
    code_size = min_code_size + 1
    output = bytearray()
    bit_buffer = 0
    bit_count = 0

    def emit(code: int) -> None:
        nonlocal bit_buffer, bit_count
        bit_buffer |= code << bit_count
        bit_count += code_size
        while bit_count >= 8:
            output.append(bit_buffer & 0xFF)
            bit_buffer >>= 8
            bit_count -= 8

    emit(clear_code)
    current = (indices[0],)
    for value in indices[1:]:
        candidate = current + (value,)
        if candidate in dictionary:
            current = candidate
            continue

        emit(dictionary[current])
        if next_code < 4096:
            dictionary[candidate] = next_code
            next_code += 1
            if next_code == (1 << code_size) + 1 and code_size < 12:
                code_size += 1
        else:
            emit(clear_code)
            dictionary = {(item,): item for item in range(clear_code)}
            next_code = end_code + 1
            code_size = min_code_size + 1
        current = (value,)

    emit(dictionary[current])
    emit(end_code)

    if bit_count:
        output.append(bit_buffer & 0xFF)
    return bytes(output)


def subblocks(data: bytes) -> bytes:
    chunks = bytearray()
    for index in range(0, len(data), 255):
        chunk = data[index : index + 255]
        chunks.append(len(chunk))
        chunks.extend(chunk)
    chunks.append(0)
    return bytes(chunks)


def write_gif(path: Path) -> None:
    min_code_size = 4
    palette_bytes = b"".join(bytes(rgb) for rgb in PALETTE)
    output = bytearray()
    output.extend(b"GIF89a")
    output.extend(WIDTH.to_bytes(2, "little"))
    output.extend(HEIGHT.to_bytes(2, "little"))
    output.extend(bytes([0xF3, 0x00, 0x00]))
    output.extend(palette_bytes)
    output.extend(b"\x21\xFF\x0BNETSCAPE2.0\x03\x01\x00\x00\x00")

    for index in range(FRAME_COUNT):
        output.extend(b"\x21\xF9\x04\x00")
        output.extend(DELAY_CS.to_bytes(2, "little"))
        output.extend(b"\x00\x00")
        output.extend(b"\x2C\x00\x00\x00\x00")
        output.extend(WIDTH.to_bytes(2, "little"))
        output.extend(HEIGHT.to_bytes(2, "little"))
        output.extend(b"\x00")
        output.append(min_code_size)
        output.extend(subblocks(pack_lzw(draw_frame(index), min_code_size)))

    output.extend(b"\x3B")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes(output))


def default_output() -> Path:
    return Path(__file__).resolve().parents[1] / "assets" / "readme-demo.gif"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the README workflow demo GIF.")
    parser.add_argument("--out", default=str(default_output()), help="Output GIF path")
    args = parser.parse_args()

    out = Path(args.out)
    write_gif(out)
    print(f"generated {out} width={WIDTH} height={HEIGHT} frames={FRAME_COUNT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
