from __future__ import annotations

from pathlib import Path

C = {
    "bg": "#020b16",
    "header": "#010810",
    "cyan": "#00e5ff",
    "magenta": "#ff00cc",
    "gold": "#ffcc00",
    "green": "#39ff14",
    "cell_a": "#081422",
    "cell_b": "#07111e",
    "grid": "#0d2d4a",
    "cop": "#1c6fe8",
    "cop_glow": "#00cfff",
    "robber": "#f59e0b",
    "robber_glow": "#ff5500",
    "barrier": "#7c2bd1",
    "white": "#e8f6ff",
    "dim": "#5a8fac",
}


def export_replay_video(
    frames: list[dict[str, object]],
    width: int,
    height: int,
    output_path: str | Path = "reports/shadowgrid_replay.mp4",
) -> Path:
    if not frames:
        raise ValueError("No frames were recorded for this game.")
    try:
        import imageio.v3 as iio
    except ImportError as exc:
        raise RuntimeError(
            "Install video dependencies with: pip install -e \".[dev,email]\""
        ) from exc

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = _render_replay_frames(frames, width, height)
    try:
        iio.imwrite(path, rendered, fps=1.8)
        return path
    except Exception:
        gif_path = path.with_suffix(".gif")
        iio.imwrite(gif_path, rendered, duration=620, loop=0)
        return gif_path


def export_replay_gif(
    frames: list[dict[str, object]],
    width: int,
    height: int,
    output_path: str | Path = "reports/shadowgrid_replay_readme.gif",
) -> Path:
    if not frames:
        raise ValueError("No frames were recorded for this game.")
    try:
        import imageio.v3 as iio
    except ImportError as exc:
        raise RuntimeError(
            "Install video dependencies with: pip install -e \".[dev,email]\""
        ) from exc

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = _render_replay_frames(frames, width, height)
    iio.imwrite(path, rendered, duration=620, loop=0)
    return path


def _render_replay_frames(frames: list[dict[str, object]], width: int, height: int):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise RuntimeError(
            "Install video dependencies with: pip install -e \".[dev,email]\""
        ) from exc

    rendered = []
    for frame in _expand_presentation_frames(frames):
        rendered.append(_render_frame(frame, width, height, Image, ImageDraw, ImageFont))
    return rendered


def _expand_presentation_frames(frames: list[dict[str, object]]) -> list[dict[str, object]]:
    expanded: list[dict[str, object]] = []
    for frame in frames:
        caption = str(frame.get("caption", ""))
        if caption.startswith("Opening:"):
            for step in range(6):
                clone = dict(frame)
                clone["caption"] = f"Curtain {step}: {caption.split(':', 1)[1].strip()}"
                expanded.append(clone)
            continue
        if caption.startswith("Game start:"):
            continue
        expanded.append(frame)
        if caption.startswith("Winner:"):
            for _ in range(10):
                expanded.append(frame)
    return expanded


def _render_frame(frame: dict[str, object], width: int, height: int, image_cls, draw_cls, font_cls):
    cell = 86
    pad = 30
    board_top = 126
    img_w = pad * 2 + width * cell
    img_h = board_top + 40 + height * cell
    image = image_cls.new("RGB", (img_w, img_h), C["bg"])
    draw = draw_cls.Draw(image)
    fonts = _fonts(font_cls)
    _draw_background(draw, img_w, img_h, board_top)
    _draw_header(draw, frame, img_w, board_top, fonts)
    _draw_board(draw, frame["state"], width, height, cell, pad, board_top, fonts)
    _draw_special_overlay(draw, frame, img_w, img_h, fonts)
    return image


def _fonts(font_cls):
    def load(size: int):
        for name in ("consola.ttf", "arial.ttf"):
            try:
                return font_cls.truetype(name, size)
            except Exception:
                pass
        return font_cls.load_default()

    return {
        "title": load(34),
        "large": load(28),
        "medium": load(16),
        "small": load(11),
        "tiny": load(9),
    }


def _draw_background(draw, img_w: int, img_h: int, board_top: int) -> None:
    draw.rectangle((0, 0, img_w, img_h), fill=C["bg"])
    for i in range(30):
        x = (i * 41) % img_w
        y = 20 + (i * 67) % max(1, img_h - 40)
        color = [C["cyan"], C["magenta"], C["gold"], C["green"]][i % 4]
        draw.ellipse((x, y, x + 3, y + 3), fill=color)
    for gx in range(0, img_w, 22):
        for gy in range(board_top, img_h, 22):
            draw.ellipse((gx, gy, gx + 2, gy + 2), fill="#0b1e30")


def _draw_header(draw, frame: dict[str, object], img_w: int, board_top: int, fonts) -> None:
    caption = str(frame.get("caption", "Agent Chase Protocol"))
    draw.rectangle((0, 0, img_w, board_top - 4), fill=C["header"])
    draw.rectangle((0, 0, img_w, 4), fill=C["magenta"])
    draw.rectangle((0, board_top - 4, img_w, board_top), fill=C["cyan"])
    draw.text((30, 24), "ShadowGrid", fill=C["gold"], font=fonts["title"])
    draw.text((30, 66), "Agent Chase Protocol", fill=C["cyan"], font=fonts["small"])
    draw.text((30, 92), caption[:72], fill=C["dim"], font=fonts["tiny"])


def _draw_board(
    draw,
    state: dict[str, object],
    width: int,
    height: int,
    cell: int,
    pad: int,
    board_top: int,
    fonts,
) -> None:
    barriers = {(p["x"], p["y"]) for p in state["barriers"]}
    for y in range(height):
        for x in range(width):
            left = pad + x * cell
            top = board_top + y * cell
            fill = C["cell_a"] if (x + y) % 2 == 0 else C["cell_b"]
            draw.rectangle(
                (left + 2, top + 2, left + cell - 7, top + cell - 7),
                fill=fill,
                outline=C["grid"],
                width=1,
            )
            draw.text((left + 8, top + 8), f"{x},{y}", fill="#152a3e", font=fonts["tiny"])
            for dx, dy in ((4, 4), (cell - 12, 4), (4, cell - 12), (cell - 12, cell - 12)):
                draw.ellipse((left + dx, top + dy, left + dx + 2, top + dy + 2), fill=C["grid"])
            if (x, y) in barriers:
                _draw_barrier(draw, left, top, cell, fonts)
    thief = state["thief"]
    cop = state["cop"]
    _draw_robber(draw, pad + thief["x"] * cell, board_top + thief["y"] * cell, cell, fonts)
    _draw_cop(draw, pad + cop["x"] * cell, board_top + cop["y"] * cell, cell, fonts)


def _draw_cop(draw, left: int, top: int, cell: int, fonts) -> None:
    cx = left + cell // 2 - 3
    cy = top + cell // 2 - 4
    for r, color in ((40, "#042036"), (32, "#063a55"), (25, "#075271")):
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)
    draw.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=C["cop"], outline=C["cyan"], width=3)
    draw.ellipse((cx - 17, cy - 17, cx + 17, cy + 17), outline="#a8deff", width=1)
    draw.text((cx - 13, cy - 8), "COP", fill="#ffffff", font=fonts["tiny"])
    draw.text((cx - 7, cy + 6), "AI", fill=C["cyan"], font=fonts["tiny"])


def _draw_robber(draw, left: int, top: int, cell: int, fonts) -> None:
    cx = left + cell // 2 - 3
    cy = top + cell // 2 - 4
    for r, color in ((40, "#351505"), (32, "#522005"), (25, "#742c05")):
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)
    pts = [(cx, cy - 24), (cx + 24, cy), (cx, cy + 24), (cx - 24, cy)]
    draw.polygon(pts, fill=C["robber"], outline=C["gold"])
    draw.text((cx - 12, cy - 8), "ROB", fill="#ffffff", font=fonts["tiny"])
    draw.text((cx - 11, cy + 6), "RUN", fill=C["robber_glow"], font=fonts["tiny"])


def _draw_barrier(draw, left: int, top: int, cell: int, fonts) -> None:
    cx = left + cell // 2 - 3
    cy = top + cell // 2 - 4
    pts = [(cx, cy - 22), (cx + 20, cy + 11), (cx - 20, cy + 11)]
    draw.polygon(pts, fill=C["barrier"], outline=C["magenta"])
    draw.text((cx - 16, cy), "BLOCK", fill="#ffffff", font=fonts["tiny"])


def _draw_special_overlay(draw, frame: dict[str, object], img_w: int, img_h: int, fonts) -> None:
    caption = str(frame.get("caption", ""))
    if caption.startswith(("Curtain", "Opening:", "Game start:")):
        if caption.startswith("Curtain"):
            try:
                step = int(caption.split(":", 1)[0].split()[1])
            except Exception:
                step = 0
            player_text = caption.split(":", 1)[-1].strip()
        else:
            step = 5
            player_text = caption.split(":", 1)[-1].strip()
        curtain = int((img_w / 2) * max(0, 5 - step) / 5)
        if curtain:
            draw.rectangle((0, 0, curtain, img_h), fill="#000a14", outline=C["cyan"], width=4)
            draw.rectangle(
                (img_w - curtain, 0, img_w, img_h),
                fill="#000a14",
                outline=C["cyan"],
                width=4,
            )
        draw.rectangle((52, 210, img_w - 52, 385), fill="#010c18", outline=C["gold"], width=4)
        draw.text((img_w / 2 - 105, 246), "GAME START", fill=C["gold"], font=fonts["large"])
        draw.text((img_w / 2 - 170, 300), player_text, fill=C["white"], font=fonts["medium"])
        draw.text(
            (img_w / 2 - 145, 340),
            "ShadowGrid Protocol Initiated",
            fill=C["green"],
            font=fonts["small"],
        )
    if caption.startswith("Winner:"):
        winner = caption.split(":", 1)[-1].strip()
        color = C["cop_glow"] if winner.lower() == "cop" else C["robber_glow"]
        draw.rectangle((0, 0, img_w, img_h), fill="#000000")
        for i in range(36):
            x = 35 + (i * 47) % max(1, img_w - 70)
            y = 70 + (i * 31) % max(1, img_h - 140)
            pc = [C["cyan"], C["magenta"], C["gold"], C["green"]][i % 4]
            draw.rectangle((x, y, x + 7, y + 7), fill=pc)
        draw.rectangle((70, 220, img_w - 70, 420), fill="#010c18", outline=color, width=5)
        draw.text((img_w / 2 - 95, 260), "GAME OVER", fill=C["gold"], font=fonts["large"])
        draw.text((img_w / 2 - 88, 318), f"{winner.upper()} WINS", fill=color, font=fonts["medium"])
        draw.text(
            (img_w / 2 - 155, 365),
            "Saved replay stops on this final board.",
            fill=C["white"],
            font=fonts["small"],
        )
