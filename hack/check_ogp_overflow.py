#!/usr/bin/env python3
"""
Detect OGP title overflow by emulating layouts/partials/ogp-image.html.

Template facts (1200x630):
- Title wrapping: English (titles containing spaces) wrap by words at ~32 chars; CJK wraps every 18 chars.
- Title font: Mplus1Code Bold 52pt; single-line English uses 72pt. Line spacing adds +18px between lines.
- Separator: 30px high; placed +20px under the title; meta starts +40px under separator.
- Meta block: 4 lines (date/author/lang/site) using 24pt Regular, vertical step 30px.
- Vertical positions: startY = ((630 - (titleHeight + separatorHeight + metaHeightConst)) // 2) + 15, clamped to a minimum of 40. metaHeightConst is 120 per template.

Detection rules:
- startY clamped -> flag as tight vertical fit.
- meta_end > 630 -> overflow.
- startY clamped AND meta_end > 580 -> overflow (no bottom margin).

Limits:
- Requires Pillow; exits 2 if missing.
- Fonts download on first run into hack/.cache/ogp-fonts/.
"""

from __future__ import annotations

import sys
import json
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from PIL import ImageFont, ImageDraw, Image
except Exception as exc:  # pragma: no cover - import gate
    print(
        "[ERROR] Pillow is missing. Run 'uv run --with pillow hack/check_ogp_overflow.py' or 'pip install Pillow'.",
        file=sys.stderr,
    )
    sys.exit(2)


ROOT_DIR = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT_DIR / "content"
FONT_CACHE = Path(__file__).resolve().parent / ".cache" / "ogp-fonts"
FONT_LOCAL_DIR = ROOT_DIR / "assets" / "fonts" / "ogp"

IMAGE_HEIGHT = 630
TITLE_FONT_SIZE = 52
TITLE_FONT_SIZE_SINGLE_EN = 72
TITLE_LINE_SPACING = 18
SEPARATOR_HEIGHT = 30
META_HEIGHT_CONST = 120
START_Y_OFFSET = 15
MIN_START_Y = 40
META_FONT_SIZE = 24
META_LINE_STEP = 30
POST_META_LINES = 4  # date, author, lang, site
SAFE_META_END = 580

FONT_URL_BOLD = "https://github.com/coz-m/MPLUS_FONTS/raw/refs/heads/master/fonts/ttf/Mplus1Code-Bold.ttf"
FONT_URL_REGULAR = "https://github.com/coz-m/MPLUS_FONTS/raw/refs/heads/master/fonts/ttf/Mplus1Code-Regular.ttf"


def download_font(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return dest
    try:
        with urllib.request.urlopen(url) as resp, dest.open("wb") as f:
            f.write(resp.read())
        return dest
    except Exception as exc:  # pragma: no cover - network dependent
        print(f"[ERROR] Failed to download font: {url}\n{exc}", file=sys.stderr)
        raise


def load_fonts() -> Dict[str, ImageFont.FreeTypeFont]:
    # Prefer vendored fonts under assets/fonts/ogp; fallback to cached download.
    bold_local = FONT_LOCAL_DIR / "Mplus1Code-Bold.ttf"
    regular_local = FONT_LOCAL_DIR / "Mplus1Code-Regular.ttf"

    if bold_local.exists() and regular_local.exists():
        bold_path, regular_path = bold_local, regular_local
    else:
        try:
            bold_path = download_font(FONT_URL_BOLD, FONT_CACHE / "Mplus1Code-Bold.ttf")
            regular_path = download_font(FONT_URL_REGULAR, FONT_CACHE / "Mplus1Code-Regular.ttf")
        except Exception:
            sys.exit(2)

    return {
        "title": ImageFont.truetype(str(bold_path), TITLE_FONT_SIZE),
        "title_single_en": ImageFont.truetype(str(bold_path), TITLE_FONT_SIZE_SINGLE_EN),
        "title_single_en_small": ImageFont.truetype(str(bold_path), 64),
        "title_force_single": ImageFont.truetype(str(bold_path), 60),
        "meta": ImageFont.truetype(str(regular_path), META_FONT_SIZE),
    }


def measure_text_width(font: ImageFont.FreeTypeFont, text: str) -> int:
    # Use ImageDraw to obtain accurate pixel width for the given font.
    img = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def extract_title(path: Path) -> str | None:
    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith("title:"):
                    val = stripped[len("title:") :].strip()
                    if (val.startswith('"') and val.endswith('"')) or (
                        val.startswith("'") and val.endswith("'")
                    ):
                        val = val[1:-1]
                    return val
    except UnicodeDecodeError:
        print(f"[WARN] Cannot read as UTF-8: {path}", file=sys.stderr)
    return None


def has_single_line_flag(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8") as f:
            lines = list(f)
    except UnicodeDecodeError:
        return False
    if not lines or not lines[0].startswith("---"):
        return False
    # parse front matter until the next '---'
    for line in lines[1:]:
        if line.startswith("---"):
            break
        if line.strip().lower().startswith("ogp_single_line:"):
            val = line.split(":", 1)[1].strip().lower()
            return val in {"true", "yes", "on", "1"}
    return False


def split_title_lines(title: str, force_single: bool) -> List[str]:
    if force_single:
        return [title]

    if " " in title:
        max_chars = 26
        words = title.split(" ")
        lines: List[str] = []
        current = ""
        for word in words:
            test = f"{current} {word}".strip() if current else word
            if len(test) > max_chars:
                if current:
                    lines.append(current)
                    current = word
                else:
                    current = word
            else:
                current = test
        if current:
            lines.append(current)
        return lines

    max_chars = 18
    return [title[i : i + max_chars] for i in range(0, len(title), max_chars)] or [title]


def line_height(font: ImageFont.FreeTypeFont, text: str) -> int:
    bbox = font.getbbox(text)
    return bbox[3] - bbox[1]


def compute_layout(title: str, fonts: Dict[str, ImageFont.FreeTypeFont], force_single: bool = False) -> Dict[str, int | float | bool | List[str]]:
    lines = split_title_lines(title, force_single=force_single)
    is_single_english = len(lines) == 1 and (" " in title)
    title_runes = len(title)

    if force_single:
        title_font = fonts["title_force_single"]
    elif is_single_english:
        if title_runes >= 24:
            title_font = fonts["title_single_en_small"]
        else:
            title_font = fonts["title_single_en"]
    else:
        title_font = fonts["title"]

    per_line_heights = [line_height(title_font, line or " ") for line in lines]
    title_height = sum(per_line_heights)
    if len(lines) > 1:
        title_height += TITLE_LINE_SPACING * (len(lines) - 1)

    available_width = 1200 - 2 * 60  # x is fixed at 60 in template
    max_line_width = max(measure_text_width(title_font, line or " ") for line in lines)

    subtitle_height = 0  # Home/About are out of scope, so keep 0

    template_total_height = title_height + subtitle_height + SEPARATOR_HEIGHT + META_HEIGHT_CONST
    unclamped_start_y = ((IMAGE_HEIGHT - template_total_height) // 2) + START_Y_OFFSET
    start_y = max(unclamped_start_y, MIN_START_Y)

    separator_y = start_y + title_height + subtitle_height + 20
    meta_y = separator_y + 40

    meta_line_height = line_height(fonts["meta"], "Ag")
    meta_block_height = meta_line_height + (POST_META_LINES - 1) * META_LINE_STEP
    meta_end = meta_y + meta_block_height

    issues: List[str] = []
    if unclamped_start_y < MIN_START_Y:
        issues.append("startY_clamped")
    if meta_end > IMAGE_HEIGHT:
        issues.append("meta_overflow")
    if start_y == MIN_START_Y and meta_end > SAFE_META_END:
        issues.append("tight_bottom_margin")
    if max_line_width > available_width:
        issues.append("horizontal_overflow")

    return {
        "lines": lines,
        "is_single_english": is_single_english,
        "title_height": title_height,
        "max_line_width": max_line_width,
        "unclamped_start_y": unclamped_start_y,
        "start_y": start_y,
        "separator_y": separator_y,
        "meta_y": meta_y,
        "meta_end": meta_end,
        "issues": issues,
    }


def has_custom_ogp(md_path: Path) -> bool:
    return (md_path.parent / "ogp.png").exists()


def is_target_file(md_path: Path) -> bool:
    if md_path.name in {"_index.md", "_index.en.md"}:
        return False
    try:
        rel = md_path.relative_to(CONTENT_DIR)
    except ValueError:
        return False
    return rel.parts and rel.parts[0] in {"post", "tmp"}


def scan_files() -> List[Path]:
    return sorted([p for p in CONTENT_DIR.rglob("*.md") if is_target_file(p)])


def main() -> int:
    fonts = load_fonts()

    md_files = scan_files()
    checked = 0
    found = 0

    for md in md_files:
        if has_custom_ogp(md):
            continue

        title = extract_title(md)
        if not title:
            print(f"[WARN] title not found: {md}", file=sys.stderr)
            continue

        force_single = has_single_line_flag(md)

        checked += 1
        layout = compute_layout(title, fonts, force_single=force_single)
        issues = layout["issues"]
        if issues:
            found += 1
            print(f"[OVERFLOW] {md}")
            print(f"  title        : {title}")
            print(f"  lines        : {len(layout['lines'])} -> {' / '.join(layout['lines'])}")
            print(
                "  title_height : "
                f"{layout['title_height']}px (single_en={layout['is_single_english']})"
            )
            print(f"  max_width    : {layout['max_line_width']}px (limit 1080px)")
            print(
                "  y-positions  : "
                f"startY={layout['start_y']} (unclamped={layout['unclamped_start_y']}), "
                f"meta_end={layout['meta_end']}"
            )
            print(f"  reasons      : {', '.join(issues)}")
            print()

    print("================================")
    print(f"Checked: {checked} files")
    if found:
        print(f"Found : {found} issue(s)")
        return 1
    print("No issues found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
