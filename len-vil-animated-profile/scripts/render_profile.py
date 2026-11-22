#!/usr/bin/env python3
"""Render Lenvil's animated, self-contained GitHub profile SVG cards."""
from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

try:
    from PIL import Image, ImageEnhance, ImageOps
except ImportError:  # Portrait becomes initials if Pillow is not installed.
    Image = None

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "cards"
DATA = ROOT / "data" / "contributions.json"
PHOTO = ROOT / "assets" / "portrait.jpg"
STATIC = os.getenv("STATIC", "0") == "1"

INK = "#20262d"
MUTED = "#66717b"
PAPER = "#f3efe5"
WHITE = "#fffdf7"
LINE = "#d9d2c5"
BLUE = "#3768d7"
CORAL = "#db765e"
YELLOW = "#e3b64b"
GREEN = "#4b936e"


def anim_style() -> str:
    if STATIC:
        return ""
    return """<style>
      .reveal{opacity:0;animation:rise .8s cubic-bezier(.2,.7,.2,1) forwards}
      .d1{animation-delay:.15s}.d2{animation-delay:.35s}.d3{animation-delay:.55s}
      .pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2.8s ease-in-out infinite}
      .shine{animation:shine 5s ease-in-out infinite}
      @keyframes rise{from{opacity:0;transform:translateY(13px)}to{opacity:1;transform:translateY(0)}}
      @keyframes pulse{0%,100%{opacity:.55;transform:scale(.92)}50%{opacity:1;transform:scale(1.08)}}
      @keyframes shine{0%,72%,100%{transform:translateX(-360px);opacity:0}78%{opacity:.55}90%{transform:translateX(780px);opacity:0}}
      @media(prefers-reduced-motion:reduce){.reveal,.pulse,.shine{animation:none!important;opacity:1!important;transform:none!important}}
    </style>"""


def ascii_portrait(cols: int = 42, rows: int = 24) -> list[str]:
    ramp = "  .,:-~=+*#%@"
    if Image is None or not PHOTO.exists():
        return ["LEN-VIL", "", "MCA / BUILDER"]
    image = Image.open(PHOTO).convert("L")
    # Crop toward a portrait framing while keeping the face and shoulders.
    w, h = image.size
    target = cols * 0.58 / rows
    current = w / h
    if current > target:
        crop_w = int(h * target)
        left = max(0, (w - crop_w) // 2)
        image = image.crop((left, 0, left + crop_w, h))
    else:
        crop_h = int(w / target)
        top = max(0, int((h - crop_h) * 0.15))
        image = image.crop((0, top, w, min(h, top + crop_h)))
    image = ImageOps.autocontrast(image)
    image = ImageEnhance.Contrast(image).enhance(1.35)
    image = image.resize((cols, rows))
    pixels = list(image.getdata())
    result = []
    for y in range(rows):
        chars = []
        for x in range(cols):
            value = pixels[y * cols + x]
            # Invert brightness: darker photo details use denser characters.
            idx = int((255 - value) / 255 * (len(ramp) - 1))
            chars.append(ramp[idx])
        result.append("".join(chars).rstrip())
    return result


def hero_svg() -> str:
    portrait = ascii_portrait()
    lines = []
    start_y = 76
    for i, line in enumerate(portrait):
        if not line:
            continue
        delay = 0 if STATIC else i * 0.035
        style = "" if STATIC else f'opacity="0" style="animation:row-in .45s {delay:.2f}s forwards"'
        lines.append(
            f'<text x="58" y="{start_y + i * 8}" fill="#52616c" font-size="7.8" letter-spacing="1.25" {style}>{escape(line)}</text>'
        )
    row_css = "" if STATIC else "<style>@keyframes row-in{to{opacity:1}}</style>"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="330" viewBox="0 0 960 330" role="img" aria-labelledby="title desc">
      <title id="title">Lenvil Pinto — MCA student and builder</title><desc id="desc">An animated ASCII portrait and introduction card in a warm editorial style.</desc>
      {anim_style()}{row_css}
      <rect width="960" height="330" rx="18" fill="{PAPER}"/>
      <rect x="16" y="16" width="928" height="298" rx="12" fill="{WHITE}" stroke="{LINE}"/>
      <path d="M470 38V292" stroke="{LINE}" stroke-width="1"/>
      <text x="40" y="43" fill="{MUTED}" font-size="10" letter-spacing="2.2" font-family="Arial,sans-serif">LEN-VIL  /  PROFILE README</text>
      <circle cx="916" cy="39" r="5" fill="{GREEN}" class="pulse"/>
      <text x="900" y="43" text-anchor="end" fill="{MUTED}" font-size="9" letter-spacing="1.5">ONLINE / LEARNING</text>
      {''.join(lines)}
      <rect x="42" y="272" width="386" height="22" rx="5" fill="#e9e3d8"/>
      <text x="54" y="287" fill="{MUTED}" font-size="9" letter-spacing="1.3">A HUMAN, NOT JUST A COMMIT HISTORY</text>
      <g class="reveal d1" font-family="Arial,sans-serif">
        <text x="510" y="91" fill="{BLUE}" font-size="12" letter-spacing="3">HELLO, I'M</text>
        <text x="505" y="143" fill="{INK}" font-size="43" font-weight="700" letter-spacing="-1.5">LENVIL PINTO</text>
        <rect x="510" y="161" width="70" height="4" rx="2" fill="{CORAL}"/>
        <text x="510" y="197" fill="{INK}" font-size="17">MCA student · curious builder</text>
        <text x="510" y="224" fill="{MUTED}" font-size="13">St. Joseph Engineering College</text>
        <text x="510" y="245" fill="{MUTED}" font-size="13">Mangaluru, India</text>
        <text x="510" y="279" fill="{BLUE}" font-size="11" letter-spacing="1.2">BUILD  /  EXPLORE  /  LEARN</text>
      </g>
      <rect x="500" y="60" width="390" height="238" rx="9" fill="none" stroke="#eee9df"/>
      <rect x="500" y="60" width="3" height="238" rx="1.5" fill="{BLUE}"/>
    </svg>'''


def load_data() -> dict | None:
    if not DATA.exists():
        return None
    try:
        return json.loads(DATA.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def contribution_svg(data: dict | None) -> str:
    days = data.get("days", []) if data else []
    by_date = {item.get("date"): item for item in days}
    # Use the exact number of returned calendar days, right-aligned in 53 columns.
    cells = []
    total_slots = 53 * 7
    if days:
        dates = sorted(by_date)
        pad = max(0, total_slots - len(dates))
        grid = [None] * pad + [by_date[d] for d in dates[-total_slots:]]
    else:
        grid = [None] * total_slots
    palette = ["#eeeae2", "#c8d9f6", "#8faee9", "#5c83dc", BLUE]
    for idx, item in enumerate(grid):
        col, row = divmod(idx, 7)
        level = int(item.get("level", 0)) if item else 0
        level = max(0, min(4, level))
        x, y = 30 + col * 13, 66 + row * 13
        delay = 0 if STATIC else idx * 0.0015
        style = "" if STATIC else f'opacity="0" style="animation:cell-in .32s {delay:.2f}s forwards"'
        cells.append(f'<rect x="{x}" y="{y}" width="9" height="9" rx="2" fill="{palette[level]}" {style}/>' )
    css = "" if STATIC else "<style>@keyframes cell-in{to{opacity:1}}</style>"

    if data:
        stats = [
            ("CONTRIBUTIONS", f"{data.get('total', 0):,}"),
            ("ACTIVE DAYS", str(data.get("active_days", 0))),
            ("CURRENT STREAK", f"{data.get('current_streak', 0)} days"),
        ]
        month_map = data.get("months", {})
        months = sorted(month_map.items())[-12:]
        max_month = max((v for _, v in months), default=1) or 1
        bar_parts = []
        for i, (month, value) in enumerate(months):
            x = 34 + i * 70
            bar_h = 28 * value / max_month
            bar_parts.append(f'<rect x="{x}" y="217" width="42" height="{bar_h:.1f}" rx="3" fill="{BLUE}" opacity=".85"/>')
            bar_parts.append(f'<text x="{x+21}" y="234" fill="{MUTED}" font-size="8" text-anchor="middle">{escape(month[5:])}</text>')
        stat_markup = ''.join(f'<text x="790" y="{76+i*37}" fill="{MUTED}" font-size="8" letter-spacing="1.3">{escape(k)}</text><text x="790" y="{96+i*37}" fill="{INK}" font-size="17" font-weight="700">{escape(v)}</text>' for i,(k,v) in enumerate(stats))
        monthly = '<text x="30" y="183" fill="{MUTED}" font-size="9" letter-spacing="1.4">MONTHLY CONTRIBUTIONS</text>'.format(MUTED=MUTED) + ''.join(bar_parts)
        update = f"LAST SYNC  /  {escape(data.get('fetched_at', ''))}"
    else:
        stat_markup = f'<text x="790" y="83" fill="{BLUE}" font-size="10" letter-spacing="1.4">LIVE DATA</text><text x="790" y="108" fill="{INK}" font-size="15" font-weight="700">Awaiting first sync</text><text x="790" y="132" fill="{MUTED}" font-size="10">No sample numbers used.</text>'
        monthly = f'<text x="30" y="183" fill="{MUTED}" font-size="9" letter-spacing="1.4">MONTHLY PULSE  /  POPULATES FROM YOUR REAL GITHUB ACTIVITY</text>'
        update = "CONTRIBUTION CALENDAR  /  REAL DATA ONLY"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="260" viewBox="0 0 960 260" role="img" aria-labelledby="title desc">
      <title id="title">GitHub contribution activity</title><desc id="desc">A contribution heatmap and monthly totals. The scheduled workflow fills it using public GitHub contribution data.</desc>
      {anim_style()}{css}<rect width="960" height="260" rx="16" fill="{PAPER}"/><rect x="16" y="16" width="928" height="228" rx="11" fill="{WHITE}" stroke="{LINE}"/>
      <text x="30" y="43" fill="{INK}" font-size="13" font-weight="700" letter-spacing="1.5">GITHUB ACTIVITY</text>
      <text x="930" y="43" fill="{MUTED}" font-size="9" text-anchor="end" letter-spacing="1.2">LAST 12 MONTHS</text>
      {''.join(cells)}
      <path d="M770 56V166" stroke="{LINE}"/>{stat_markup}
      {monthly}
      <text x="930" y="235" fill="{MUTED}" font-size="8" text-anchor="end" letter-spacing="1">{update}</text>
    </svg>'''


def about_svg() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="142" viewBox="0 0 960 142" role="img" aria-labelledby="title">
      <title id="title">About Lenvil and technology interests</title>{anim_style()}
      <rect width="960" height="142" rx="15" fill="{PAPER}"/><rect x="16" y="14" width="928" height="114" rx="10" fill="{WHITE}" stroke="{LINE}"/>
      <text x="40" y="48" fill="{BLUE}" font-size="10" letter-spacing="2">A LITTLE ABOUT ME</text>
      <text x="40" y="77" fill="{INK}" font-size="16" font-weight="700">I enjoy turning ideas into useful, working projects.</text>
      <text x="40" y="101" fill="{MUTED}" font-size="12">Currently exploring full-stack development, Flutter, AI-powered applications and practical problem-solving.</text>
      <path d="M690 32V109" stroke="{LINE}"/>
      <text x="720" y="48" fill="{MUTED}" font-size="9" letter-spacing="1.4">TOOLS I WORK WITH</text>
      <text x="720" y="72" fill="{INK}" font-size="13" font-weight="700">React · TypeScript · Flutter</text>
      <text x="720" y="95" fill="{INK}" font-size="13" font-weight="700">Python · Java · Supabase</text>
    </svg>'''


def tile_svg(title: str, number: str, subtitle: str, color: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="150" viewBox="0 0 300 150" role="img" aria-labelledby="title">
      <title id="title">{escape(title)}</title>{anim_style()}
      <rect width="300" height="150" rx="14" fill="{color}"/>
      <text x="22" y="34" fill="#ffffff" opacity=".8" font-size="10" letter-spacing="2">{escape(number)}</text>
      <text x="22" y="91" fill="#ffffff" font-size="31" font-weight="700" letter-spacing="-1">{escape(title)}</text>
      <text x="22" y="119" fill="#ffffff" opacity=".9" font-size="11">{escape(subtitle)}</text>
      <path d="M255 25l19 19-19 19" fill="none" stroke="#fff" stroke-width="2" opacity=".75"/>
      <circle cx="270" cy="118" r="17" fill="none" stroke="#fff" stroke-width="1" opacity=".25" class="pulse"/>
    </svg>'''


def projects_svg() -> str:
    projects = [
        ("01", "VARTHA", "AI-powered multilingual news access", BLUE),
        ("02", "CropGenius", "Crop insights, disease detection and market tracking", GREEN),
        ("03", "CareConnect", "Healthcare appointments and reminders", CORAL),
        ("04", "TrustLens", "A browser companion for safer browsing", "#58677d"),
        ("05", "CashVision", "Currency recognition concept", "#b58a36"),
    ]
    cards = []
    for i, (num, name, desc, color) in enumerate(projects):
        col = i % 3
        row = i // 3
        x = 22 + col * 307 if row == 0 else 176 + col * 307
        y = 56 + row * 132
        cards.append(f'''<g class="reveal d{i%3+1}">
          <rect x="{x}" y="{y}" width="286" height="108" rx="10" fill="{WHITE}" stroke="{LINE}"/>
          <rect x="{x}" y="{y}" width="5" height="108" rx="2" fill="{color}"/>
          <text x="{x+20}" y="{y+27}" fill="{color}" font-size="9" letter-spacing="1.5">PROJECT / {num}</text>
          <text x="{x+20}" y="{y+56}" fill="{INK}" font-size="19" font-weight="700">{escape(name)}</text>
          <text x="{x+20}" y="{y+79}" fill="{MUTED}" font-size="10">{escape(desc)}</text>
        </g>''')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="330" viewBox="0 0 960 330" role="img" aria-labelledby="title desc">
      <title id="title">Selected projects</title><desc id="desc">Five project highlights: VARTHA, CropGenius, CareConnect, TrustLens and CashVision.</desc>{anim_style()}
      <rect width="960" height="330" rx="16" fill="{PAPER}"/><rect x="16" y="16" width="928" height="298" rx="11" fill="{WHITE}" stroke="{LINE}"/>
      <text x="30" y="42" fill="{BLUE}" font-size="10" letter-spacing="2">SELECTED WORK / IDEAS IN PROGRESS</text>
      {''.join(cards)}
    </svg>'''


def write(name: str, content: str) -> None:
    CARDS.mkdir(parents=True, exist_ok=True)
    (CARDS / name).write_text(content, encoding="utf-8")


def main() -> None:
    write("hero.svg", hero_svg())
    write("contributions.svg", contribution_svg(load_data()))
    write("about.svg", about_svg())
    write("build.svg", tile_svg("BUILD", "01 / MAKE", "Turn ideas into useful things", BLUE))
    write("explore.svg", tile_svg("EXPLORE", "02 / TRY", "Experiment with new technology", CORAL))
    write("learn.svg", tile_svg("LEARN", "03 / GROW", "Keep improving, one step at a time", "#bd953d"))
    write("projects.svg", projects_svg())
    print(f"Rendered profile cards in {CARDS}")


if __name__ == "__main__":
    main()
