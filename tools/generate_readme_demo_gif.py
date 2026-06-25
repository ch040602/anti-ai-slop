from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

WIDTH = 960
HEIGHT = 540
FRAME_COUNT = 20
DELAY_CS = 35

PALETTE = [
    (12, 16, 23),
    (24, 31, 42),
    (43, 52, 66),
    (238, 242, 247),
    (149, 164, 184),
    (72, 133, 237),
    (38, 196, 133),
    (245, 158, 11),
    (239, 68, 68),
    (124, 92, 255),
    (14, 165, 233),
    (20, 83, 45),
    (63, 76, 96),
    (246, 248, 251),
    (147, 197, 253),
    (20, 118, 110),
]

FONT = {
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    "a": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "b": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "c": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "d": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "e": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "f": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "g": ["01111", "10000", "10000", "10011", "10001", "10001", "01111"],
    "h": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "i": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "j": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "k": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "l": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "m": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "n": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "o": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "p": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "r": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "s": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "t": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "u": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "v": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "w": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "x": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "10000", "11110", "00001", "00001", "11110"],
    "6": ["01110", "10000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00001", "01110"],
    "$": ["00100", "01111", "10100", "01110", "00101", "11110", "00100"],
    ":": ["00000", "00100", "00100", "00000", "00100", "00100", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ",": ["00000", "00000", "00000", "00000", "00100", "00100", "01000"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    "_": ["00000", "00000", "00000", "00000", "00000", "00000", "11111"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    "\\": ["10000", "01000", "01000", "00100", "00010", "00010", "00001"],
    ">": ["10000", "01000", "00100", "00010", "00100", "01000", "10000"],
    "=": ["00000", "11111", "00000", "11111", "00000", "00000", "00000"],
    "(": ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ")": ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    "[": ["01110", "01000", "01000", "01000", "01000", "01000", "01110"],
    "]": ["01110", "00010", "00010", "00010", "00010", "00010", "01110"],
    "#": ["01010", "11111", "01010", "01010", "11111", "01010", "01010"],
    "+": ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
}

def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def clean_line(line: str, limit: int = 42) -> str:
    allowed = []
    for char in line.replace("\t", "    "):
        if 32 <= ord(char) <= 126:
            allowed.append(char)
        else:
            allowed.append(" ")
    text = "".join(allowed).strip()
    return text if len(text) <= limit else text[: limit - 3] + "..."


def run_command(command: list[str], cwd: Path) -> list[str]:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    output = result.stdout if result.stdout.strip() else result.stderr
    lines = [clean_line(line) for line in output.splitlines() if clean_line(line)]
    if result.returncode != 0:
        lines.insert(0, f"exit code: {result.returncode}")
    return lines


def select_lines(lines: list[str], needles: list[str], limit: int = 3) -> list[str]:
    selected: list[str] = []
    for needle in needles:
        for line in lines:
            if needle.lower() in line.lower() and line not in selected:
                selected.append(line)
                break
    if len(selected) < limit:
        for line in lines:
            if line not in selected:
                selected.append(line)
            if len(selected) >= limit:
                break
    return selected[:limit]


def command_lines(command: str, output: list[str], output_color: int = 6) -> list[tuple[str, int]]:
    return [(command, 14)] + [(line, output_color) for line in output]


def build_scenes() -> list[dict[str, object]]:
    root = repo_root()
    check_lines = run_command(
        [
            sys.executable,
            "tools/validators/check_all.py",
            "--root",
            ".",
            "--profile",
            "pack-self",
            "--format",
            "markdown",
        ],
        root,
    )
    inventory_lines = run_command([sys.executable, "tools/repo_inventory.py", "--root", ".", "--format", "markdown"], root)

    with tempfile.TemporaryDirectory(prefix="anti-ai-slop-demo-") as tmp:
        target = Path(tmp) / "target-repo"
        target.mkdir()
        (target / "README.md").write_text("# Demo target\n", encoding="utf-8")
        apply_lines = run_command(
            [
                sys.executable,
                "tools/apply_guardrails.py",
                "--target",
                str(target),
                "--mode",
                "dry-run",
            ],
            root,
        )

    return [
        {
            "step": "validate",
            "title": "Actual: coherence validator",
            "lines": command_lines(
                "$ python tools/validators/check_all.py --root .",
                select_lines(check_lines, ["Score:", "CRITICAL:", "No findings."], 3),
            ),
        },
        {
            "step": "inventory",
            "title": "Actual: repository inventory",
            "lines": command_lines(
                "$ python tools/repo_inventory.py --root .",
                select_lines(inventory_lines, ["Files:", "`tools`", "`.md`"], 3),
            ),
        },
        {
            "step": "dry-run",
            "title": "Actual: dry-run apply to temp repo",
            "lines": command_lines(
                "$ python tools/apply_guardrails.py --mode dry-run",
                select_lines(apply_lines, ["skip existing README.md", "copy SKILL.md", "copy tools/validators/check_all.py"], 3),
            ),
        },
    ]


def fill_rect(pixels: bytearray, x: int, y: int, width: int, height: int, color: int) -> None:
    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(WIDTH, x + width)
    y2 = min(HEIGHT, y + height)
    for row in range(y1, y2):
        start = row * WIDTH + x1
        pixels[start : row * WIDTH + x2] = bytes([color]) * (x2 - x1)


def draw_text(pixels: bytearray, x: int, y: int, text: str, color: int, scale: int = 2) -> None:
    cursor = x
    for raw_char in text:
        char = raw_char.lower()
        glyph = FONT.get(char, ["11111", "10001", "00010", "00100", "00000", "00100", "00100"])
        for row, pattern in enumerate(glyph):
            for col, bit in enumerate(pattern):
                if bit == "1":
                    fill_rect(pixels, cursor + col * scale, y + row * scale, scale, scale, color)
        cursor += 6 * scale


def draw_badge(pixels: bytearray, x: int, y: int, label: str, color: int, active: bool) -> None:
    fill_rect(pixels, x, y, 176, 32, color if active else 2)
    fill_rect(pixels, x + 10, y + 10, 10, 10, 3 if active else 4)
    draw_text(pixels, x + 30, y + 9, label, 3 if active else 4, 1)


def draw_terminal(pixels: bytearray, scene: dict[str, object], reveal_count: int) -> None:
    fill_rect(pixels, 300, 112, 612, 348, 1)
    fill_rect(pixels, 300, 112, 612, 34, 2)
    fill_rect(pixels, 320, 126, 10, 10, 8)
    fill_rect(pixels, 340, 126, 10, 10, 7)
    fill_rect(pixels, 360, 126, 10, 10, 6)
    draw_text(pixels, 390, 123, str(scene["title"]), 3, 1)

    lines = scene["lines"]
    for index, (line, color) in enumerate(lines[:reveal_count]):
        draw_text(pixels, 324, 176 + index * 48, line, color, 2)
    if reveal_count < len(lines):
        y = 176 + reveal_count * 48
        fill_rect(pixels, 324, y + 2, 14, 22, 6)


def draw_frame(index: int, scenes: list[dict[str, object]]) -> bytes:
    pixels = bytearray([0]) * (WIDTH * HEIGHT)
    fill_rect(pixels, 0, 0, WIDTH, HEIGHT, 0)
    fill_rect(pixels, 0, 0, WIDTH, 76, 1)
    draw_text(pixels, 38, 24, "anti-ai-slop", 3, 3)
    draw_text(pixels, 38, 56, "rendered from actual command output", 4, 1)
    fill_rect(pixels, 824, 28, 86, 22, 6 if index == FRAME_COUNT - 1 else 7)
    draw_text(pixels, 838, 35, "ready", 3, 1)

    scene_index = min(len(scenes) - 1, index * len(scenes) // FRAME_COUNT)
    scene = scenes[scene_index]
    scene_start = scene_index * FRAME_COUNT // len(scenes)
    scene_end = (scene_index + 1) * FRAME_COUNT // len(scenes)
    scene_span = max(1, scene_end - scene_start)
    frame_in_scene = index - scene_start
    reveal_count = min(len(scene["lines"]), 1 + frame_in_scene * len(scene["lines"]) // scene_span)

    fill_rect(pixels, 40, 112, 220, 348, 1)
    draw_text(pixels, 62, 136, "workflow", 3, 2)
    steps = ["validate", "inventory", "dry-run"]
    for step_index, step in enumerate(steps):
        draw_badge(pixels, 62, 186 + step_index * 66, step, [5, 7, 10][step_index], step == scene["step"])
        if step_index < len(steps) - 1:
            fill_rect(pixels, 146, 222 + step_index * 66, 8, 28, 12)

    draw_terminal(pixels, scene, reveal_count)

    fill_rect(pixels, 300, 486, 612, 10, 12)
    progress = int(612 * ((index + 1) / FRAME_COUNT))
    fill_rect(pixels, 300, 486, progress, 10, 6)
    draw_text(pixels, 40, 492, "real stdout -> rendered gif -> repeatable demo", 4, 1)
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
    scenes = build_scenes()
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
        output.extend(subblocks(pack_lzw(draw_frame(index, scenes), min_code_size)))

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
