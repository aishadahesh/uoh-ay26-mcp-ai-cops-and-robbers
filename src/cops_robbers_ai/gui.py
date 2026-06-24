from __future__ import annotations

import json
import math
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox

from .config import load_config
from .engine import GameEngine
from .env_loader import load_dotenv
from .llm_agent import GeminiAgent
from .models import Action, Move, Position, Role
from .video_export import export_replay_gif, export_replay_video

CELL = 86
PAD = 30
BOARD_TOP = 126
WINDOW_W = 1080
WINDOW_H = 780
GAME_NAME = "ShadowGrid"
GAME_SUBTITLE = "Agent Chase Protocol"

# ── Neon Cyberpunk Palette ────────────────────────────────────────────────────
C = {
    "bg":            "#020b16",
    "panel":         "#070e1a",
    "panel2":        "#0b1526",
    "border_cyan":   "#00e5ff",
    "border_magenta":"#ff00cc",
    "border_gold":   "#ffcc00",
    "neon_green":    "#39ff14",
    "neon_blue":     "#1e90ff",
    "neon_purple":   "#c44dff",
    "cop_core":      "#1c6fe8",
    "cop_glow":      "#00cfff",
    "cop_light":     "#93d5fd",
    "rob_core":      "#f59e0b",
    "rob_glow":      "#ff5500",
    "rob_light":     "#fde68a",
    "cell_a":        "#081422",
    "cell_b":        "#07111e",
    "grid_line":     "#0d2d4a",
    "move_hint":     "#00ff88",
    "barrier_fill":  "#3b0d6b",
    "barrier_border":"#9d4edd",
    "text_white":    "#e8f6ff",
    "text_dim":      "#5a8fac",
    "text_gold":     "#fbbf24",
    "text_cyan":     "#22e8ff",
    "header_bg":     "#010810",
}

MOVE_KEYS = {
    "q": Move.NW, "w": Move.N,  "e": Move.NE,
    "a": Move.W,  "s": Move.STAY, "d": Move.E,
    "z": Move.SW, "x": Move.S,  "c": Move.SE,
}
MODE_LABELS = {
    "cop_agent_robber_user":   "Cop agent, robber user",
    "cop_user_robber_agent":   "Cop user, robber agent",
    "cop_user_robber_user":    "Cop user, robber user",
    "cop_openai_robber_gemini":"Cop OpenAI, robber Gemini",
}


def _lerp(c1: str, c2: str, t: float) -> str:
    """Linearly interpolate between two hex colours."""
    t = max(0.0, min(1.0, t))
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    return f"#{int(r1+(r2-r1)*t):02x}{int(g1+(g2-g1)*t):02x}{int(b1+(b2-b1)*t):02x}"


def _pulse(tick: int, speed: float = 1.0, lo: float = 0.0, hi: float = 1.0) -> float:
    """Smooth sine-wave oscillation."""
    return lo + (hi - lo) * (math.sin(tick * speed * 0.13) + 1) / 2


# ─────────────────────────────────────────────────────────────────────────────
class PlayApp:
    def __init__(self) -> None:
        load_dotenv()
        self.config = load_config()
        self.engine = GameEngine(self.config, seed_offset=99)
        self.state = self.engine.new_state()
        self.agents: dict[Role, GeminiAgent] = {
            "cop":   GeminiAgent("cop",   self.config.llm),
            "thief": GeminiAgent("thief", self.config.llm),
        }
        self.root = tk.Tk()
        self.mode = tk.StringVar(value="cop_agent_robber_user")
        self.current_role: Role = "thief"
        self.last_message = {"cop": "", "thief": ""}
        self.finished = False
        self.highlights: dict[tuple[int, int], Move] = {}
        self.barrier_mode = False
        self.replay_frames: list[dict[str, object]] = []
        self.movement_log: list[dict[str, object]] = []
        self.final_result: str | None = None
        self.presentation_active = False
        # animation state
        self._tick = 0
        self._curtain_end_tick = 0
        self._trail: list[tuple[int, int, str]] = []   # (x, y, colour)

        self.root.title(f"{GAME_NAME} - {GAME_SUBTITLE}")
        self.root.configure(bg=C["bg"])
        self._center_window()
        self._layout()
        self.root.bind("<Key>", self._key_move)
        self.canvas.bind("<Button-1>", self._click_board)
        self.canvas.bind("<Button-3>", self._right_click_board)
        self.reset()
        self._anim_loop()

    # ── animation heartbeat ──────────────────────────────────────────────────
    def _anim_loop(self) -> None:
        self._tick += 1
        self.draw()
        self.root.after(55, self._anim_loop)

    # ── layout ───────────────────────────────────────────────────────────────
    def _layout(self) -> None:
        shell = tk.Frame(self.root, bg=C["bg"])
        shell.pack(expand=True, anchor="center", padx=10, pady=10)
        shell.grid_columnconfigure(0, weight=1)
        shell.grid_columnconfigure(1, weight=1)

        board_w = CELL * 5 + PAD * 2
        board_h = CELL * 5 + BOARD_TOP + 40
        self.canvas = tk.Canvas(shell, width=board_w, height=board_h,
                                bg=C["bg"], highlightthickness=0)
        self.canvas.grid(row=0, column=0, padx=12, pady=10, sticky="n")

        # Neon-bordered side panel
        border_frame = tk.Frame(shell, bg=C["border_cyan"], padx=2, pady=2)
        border_frame.grid(row=0, column=1, padx=12, pady=10, sticky="n")
        side = tk.Frame(border_frame, bg=C["panel"])
        side.pack()
        inner = tk.Frame(side, bg=C["panel"], padx=16, pady=16)
        inner.pack()

        # Title
        tk.Label(inner, text=GAME_NAME, bg=C["panel"], fg=C["text_gold"],
                 font=("Consolas", 22, "bold")).pack(anchor="w")
        tk.Label(inner, text=GAME_SUBTITLE, bg=C["panel"], fg=C["border_cyan"],
                 font=("Consolas", 9, "bold")).pack(anchor="w", pady=(0, 6))
        tk.Frame(inner, bg=C["border_cyan"], height=2).pack(fill="x", pady=(0, 8))

        self.status = tk.Label(inner, bg=C["panel"], fg=C["text_white"],
                               font=("Consolas", 13, "bold"))
        self.status.pack(anchor="w")
        self.substatus = tk.Label(inner, bg=C["panel"], fg=C["text_cyan"],
                                  font=("Consolas", 9))
        self.substatus.pack(anchor="w", pady=(2, 8))

        tk.Frame(inner, bg=C["neon_purple"], height=1).pack(fill="x", pady=(0, 8))

        self.legend = tk.Label(inner, bg=C["panel"], fg=C["text_dim"],
                               justify="left", font=("Consolas", 9))
        self.legend.pack(anchor="w", pady=(0, 8))

        tk.Frame(inner, bg=C["border_cyan"], height=1).pack(fill="x", pady=(0, 10))

        btns = tk.Frame(inner, bg=C["panel"])
        btns.pack(fill="x", pady=(0, 10))
        self._neon_btn(btns, "New Game", self.reset, C["rob_glow"], "#050000"
                       ).grid(row=0, column=0, padx=(0, 6), pady=2)
        self._neon_btn(btns, "Save Game", self.save_game, C["border_cyan"], "#010810"
                       ).grid(row=0, column=1, pady=2)

        self._mode_picker(inner)
        self._action_pad(inner)

        log_border = tk.Frame(inner, bg=C["border_cyan"], padx=1, pady=1)
        log_border.pack(pady=(10, 4), fill="x")
        self.log = tk.Text(log_border, width=44, height=9, bg="#00060f",
                           fg=C["neon_green"], wrap="word",
                           insertbackground="#fff", relief="flat",
                           font=("Consolas", 9))
        self.log.pack()

    def _neon_btn(self, parent, text: str, cmd, bg: str, fg: str) -> tk.Button:
        return tk.Button(parent, text=text, command=cmd,
                         bg=bg, fg=fg, activebackground=C["border_gold"],
                         activeforeground="#000", width=16, relief="flat",
                         font=("Consolas", 9, "bold"), cursor="hand2")

    def _center_window(self) -> None:
        self.root.update_idletasks()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{WINDOW_W}x{WINDOW_H}+{max(0,(sw-WINDOW_W)//2)}+{max(0,(sh-WINDOW_H)//2)}")
        self.root.minsize(1000, 720)

    def _mode_picker(self, parent: tk.Frame) -> None:
        box = tk.LabelFrame(parent, text=" Play Mode ", bg=C["panel"], fg=C["text_cyan"],
                            padx=10, pady=8, font=("Consolas", 9, "bold"), highlightthickness=0)
        box.pack(fill="x", pady=(0, 10))
        for value, label in MODE_LABELS.items():
            tk.Radiobutton(box, text=label, value=value, variable=self.mode,
                           command=self.reset, bg=C["panel"], fg=C["text_white"],
                           selectcolor="#180a30", activebackground=C["panel"],
                           activeforeground=C["text_gold"],
                           font=("Consolas", 9)).pack(anchor="w")

    def _action_pad(self, parent: tk.Frame) -> None:
        box = tk.LabelFrame(parent, text=" Move Pad ", bg=C["panel"], fg=C["text_cyan"],
                            padx=8, pady=8, font=("Consolas", 9, "bold"))
        box.pack(fill="x")
        dirs = [("NW", Move.NW), ("N", Move.N), ("NE", Move.NE),
                ("W", Move.W), ("WAIT", Move.STAY), ("E", Move.E),
                ("SW", Move.SW), ("S", Move.S), ("SE", Move.SE)]
        for i, (lbl, mv) in enumerate(dirs):
            bg = C["cop_core"] if i != 4 else "#0d1a32"
            tk.Button(box, text=lbl, width=8, height=2, bg=bg, fg=C["text_white"],
                      activebackground=C["neon_green"], activeforeground="#000",
                      relief="flat", font=("Consolas", 8, "bold"), cursor="hand2",
                      command=lambda m=mv: self.user_move(m)
                      ).grid(row=i // 3, column=i % 3, padx=3, pady=3)
        self.barrier_button = tk.Button(
            box, text="Place Barrier",
            bg=C["neon_purple"], fg="#fff",
            activebackground=C["border_magenta"], activeforeground="#000",
            relief="flat", font=("Consolas", 9, "bold"), cursor="hand2",
            command=self.place_barrier)
        self.barrier_button.grid(row=3, column=0, columnspan=3,
                                 sticky="ew", padx=3, pady=(6, 0))

    # ── game logic ───────────────────────────────────────────────────────────
    def reset(self) -> None:
        self.engine = GameEngine(self.config, seed_offset=99)
        self.state = self.engine.new_state()
        self.current_role = "thief"
        self.last_message = {"cop": "The robber moves first.", "thief": "The chase begins."}
        self.finished = False
        self.barrier_mode = False
        self.replay_frames = []
        self.movement_log = []
        self.final_result = None
        self.presentation_active = True
        self._trail = []
        self._curtain_end_tick = self._tick + 16   # ~880 ms of curtain
        self._configure_agents_for_mode()
        self.log.delete("1.0", "end")
        self._log("New game started. Robber moves first.")
        self._record_frame(f"Opening: {self._players_text()}")
        for step in range(6):
            self._record_frame(f"Curtain {step}: {self._players_text()}")

    def user_move(self, move: Move) -> None:
        if self.presentation_active or self.finished or not self._is_human_turn():
            return
        if move == Move.BARRIER:
            self.place_barrier()
            return
        legal = self._legal_moves(self.current_role)
        if move not in legal.values():
            self._log("That move is not available from this square.")
            return
        self._apply_user_action(move)

    def place_barrier(self) -> None:
        if self.finished or self.current_role != "cop" or not self._is_human_turn():
            return
        self._apply_user_action(Move.BARRIER)

    def ai_turn(self) -> None:
        if self.presentation_active or self.finished or self._is_human_turn():
            return
        role = self.current_role
        self._configure_agents_for_mode()
        observation = self.state.visible_to(role, self.config.visibility_radius)
        action = self.agents[role].choose(observation, self.last_message[role])
        action = self._sanitize_ai_action(action)
        # trail
        src = self.state.cop if role == "cop" else self.state.thief
        clr = C["cop_glow"] if role == "cop" else C["rob_glow"]
        self._trail.append((src.x, src.y, clr))
        if len(self._trail) > 6:
            self._trail.pop(0)
        self.engine.apply(self.state, action)
        self.last_message[self._other(role)] = action.message
        self._log(f"{role.title()} AI -> {action.move.value}: {action.message[:60]}")
        self._record_move(role, "agent", action.move, action.message)
        self._record_frame(f"{role.title()} AI moved {action.move.value}")
        self._after_turn()

    # ── master draw ──────────────────────────────────────────────────────────
    def draw(self) -> None:
        self.canvas.delete("all")
        self.highlights = self._legal_moves(self.current_role) if self._is_human_turn() else {}
        self._draw_bg()
        self._draw_header()
        self._draw_board()
        self._draw_trail()
        self._draw_pieces()
        self._update_status()
        # curtain animation (driven by tick counter)
        if self.presentation_active:
            self._draw_curtain()
            if self._tick >= self._curtain_end_tick:
                self.presentation_active = False
                self._record_frame(f"Game start: {self._players_text()}")
                self._advance_ai_if_needed()
        # end overlay (re-drawn every frame so it stays on screen)
        if self.finished and self.final_result:
            winner = "Cop" if self.final_result == "cop_wins" else "Robber"
            self._draw_end_overlay(winner)

    # ── background ───────────────────────────────────────────────────────────
    def _draw_bg(self) -> None:
        w = CELL * 5 + PAD * 2
        h = CELL * 5 + BOARD_TOP + 40
        self.canvas.create_rectangle(0, 0, w, h, fill=C["bg"], outline="")
        for i in range(24):
            x = (i * 41 + self._tick * (2 + i % 3)) % w
            y = 22 + ((i * 67 + self._tick * (1 + i % 2)) % max(1, h - 42))
            col = [C["border_cyan"], C["border_magenta"], C["border_gold"], C["neon_green"]][i % 4]
            size = 2 + i % 3
            self.canvas.create_oval(x, y, x + size, y + size, fill=col, outline="")
        scan_y = BOARD_TOP + (self._tick * 5) % max(1, h - BOARD_TOP)
        self.canvas.create_rectangle(0, scan_y, w, scan_y + 3,
                                     fill=_lerp(C["bg"], C["border_cyan"], 0.5), outline="")
        # subtle cyber dot-grid below the board area
        for gx in range(0, w, 22):
            for gy in range(BOARD_TOP, h, 22):
                self.canvas.create_oval(gx, gy, gx + 2, gy + 2, fill="#0b1e30", outline="")

    # ── header ───────────────────────────────────────────────────────────────
    def _draw_header(self) -> None:
        w = CELL * 5 + PAD * 2

        # Dark header background with magenta top stripe
        self.canvas.create_rectangle(0, 0, w, BOARD_TOP - 4, fill=C["header_bg"], outline="")
        self.canvas.create_rectangle(0, 0, w, 4, fill=C["border_magenta"], outline="")

        # Animated accent bar (colour cycles cyan ↔ magenta)
        bar_t = _pulse(self._tick, 0.7)
        bar_col = _lerp(C["border_cyan"], C["border_magenta"], bar_t)
        self.canvas.create_rectangle(0, BOARD_TOP - 4, w, BOARD_TOP, fill=bar_col, outline="")

        # Title with layered glow shadow
        title_t = _pulse(self._tick, 0.5)
        shadow_col = _lerp(C["rob_glow"], C["text_gold"], title_t)
        for off in (3, 2, 1):
            self.canvas.create_text(PAD + off, 32 + off, anchor="w", text=GAME_NAME,
                                    fill=shadow_col, font=("Consolas", 26, "bold"))
        self.canvas.create_text(PAD, 32, anchor="w", text=GAME_NAME,
                                fill=C["text_gold"], font=("Consolas", 26, "bold"))

        self.canvas.create_text(PAD, 66, anchor="w", text=GAME_SUBTITLE,
                                fill=C["border_cyan"], font=("Consolas", 11, "bold"))
        self.canvas.create_text(PAD, 92, anchor="w", text=MODE_LABELS[self.mode.get()],
                                fill=C["text_dim"], font=("Consolas", 10))

        # Animated turn badge
        badge_t = _pulse(self._tick, 1.6)
        if self.current_role == "thief":
            badge_fill = _lerp(C["rob_core"], C["rob_glow"], badge_t)
            badge_label = "ROBBER TURN"
            badge_fg = "#060100"
        else:
            badge_fill = _lerp(C["cop_core"], C["cop_glow"], badge_t)
            badge_label = "COP TURN"
            badge_fg = "#000810"

        bx1, by1, bx2, by2 = w - 218, 18, w - 14, 70
        # multi-layer glow halo
        for exp in (14, 9, 4):
            halo = _lerp(C["bg"], badge_fill, 1 - exp / 18)
            self.canvas.create_rectangle(bx1 - exp, by1 - exp, bx2 + exp, by2 + exp,
                                         fill=halo, outline="")
        self.canvas.create_rectangle(bx1, by1, bx2, by2,
                                     fill=badge_fill, outline="#ffffff", width=2)
        self.canvas.create_text((bx1 + bx2) / 2, (by1 + by2) / 2,
                                text=badge_label, fill=badge_fg,
                                font=("Consolas", 12, "bold"))

        # Move counter (top-right)
        moves_done = self.state.turn_index // 2
        self.canvas.create_text(w - 116, 90,
                                text=f"MOVE {moves_done}/{self.config.max_moves}",
                                fill=C["neon_green"], font=("Consolas", 9, "bold"), anchor="center")

    # ── board ────────────────────────────────────────────────────────────────
    def _draw_board(self) -> None:
        for y in range(self.state.height):
            for x in range(self.state.width):
                left, top = self._cell_origin(x, y)
                is_hi = (x, y) in self.highlights

                # Cell fill
                if is_hi:
                    hi_t = _pulse(self._tick, 2.2)
                    cell_col = _lerp("#041a0c", "#083520", hi_t)
                    out_col   = _lerp(C["move_hint"], "#00ffaa", hi_t)
                    out_w = 2
                else:
                    cell_col = C["cell_a"] if (x + y) % 2 == 0 else C["cell_b"]
                    out_col  = C["grid_line"]
                    out_w = 1

                self.canvas.create_rectangle(left + 2, top + 2,
                                             left + CELL - 7, top + CELL - 7,
                                             fill=cell_col, outline=out_col, width=out_w)

                # Tiny corner dots
                dot_col = out_col
                for dx, dy in ((3, 3), (CELL - 11, 3), (3, CELL - 11), (CELL - 11, CELL - 11)):
                    self.canvas.create_oval(left + dx, top + dy,
                                           left + dx + 2, top + dy + 2,
                                           fill=dot_col, outline="")

                # Coordinate label
                coord_col = C["move_hint"] if is_hi else "#152a3e"
                self.canvas.create_text(left + 8, top + 9, text=f"{x},{y}",
                                        fill=coord_col, font=("Consolas", 7, "bold"), anchor="w")

                # Pulsing ring for legal moves
                if is_hi:
                    cx = left + CELL // 2 - 3
                    cy = top + CELL // 2 - 3
                    r_t = _pulse(self._tick, 2.8)
                    ring_r = int(14 + r_t * 8)
                    ring_col = _lerp(C["move_hint"], "#00ffaa", r_t)
                    for ring in (ring_r + 8, ring_r + 4, ring_r):
                        fade = _lerp(cell_col, ring_col, ring / (ring_r + 12))
                        self.canvas.create_oval(cx - ring, cy - ring,
                                               cx + ring, cy + ring,
                                               fill="", outline=fade, width=1)
                    self.canvas.create_oval(cx - ring_r, cy - ring_r,
                                           cx + ring_r, cy + ring_r,
                                           fill="#031a0a", outline=ring_col, width=2)
                    mv_lbl = self.highlights[(x, y)].value.upper()
                    self.canvas.create_text(cx, cy, text=mv_lbl,
                                           fill=ring_col, font=("Consolas", 8, "bold"))

    # ── movement trails ──────────────────────────────────────────────────────
    def _draw_trail(self) -> None:
        n = len(self._trail)
        for i, (tx, ty, colour) in enumerate(self._trail):
            left, top = self._cell_origin(tx, ty)
            cx = left + CELL // 2 - 3
            cy = top + CELL // 2 - 4
            alpha = (i + 1) / n
            fade = _lerp(C["bg"], colour, alpha * 0.30)
            r = int(8 + alpha * 16)
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                   fill=fade, outline="")

    # ── pieces ───────────────────────────────────────────────────────────────
    def _draw_pieces(self) -> None:
        for b in self.state.barriers:
            self._draw_barrier(b.x, b.y)
        self._draw_thief(self.state.thief.x, self.state.thief.y)
        self._draw_cop(self.state.cop.x, self.state.cop.y)

    def _draw_cop(self, x: int, y: int) -> None:
        left, top = self._cell_origin(x, y)
        cx = left + CELL // 2 - 3
        cy = top + CELL // 2 - 4
        pt = _pulse(self._tick, 1.1)
        glow = _lerp(C["cop_core"], C["cop_glow"], pt)
        # Glow halos
        for r, strength in ((40, 0.06), (32, 0.13), (25, 0.25)):
            hc = _lerp(C["bg"], glow, strength)
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=hc, outline="")
        # Drop shadow
        self.canvas.create_oval(cx - 22 + 3, cy - 22 + 4, cx + 22 + 3, cy + 22 + 4,
                               fill="#000000", outline="")
        # Body
        self.canvas.create_oval(cx - 22, cy - 22, cx + 22, cy + 22,
                               fill=glow, outline=C["border_cyan"], width=3)
        # Inner badge ring
        self.canvas.create_oval(cx - 17, cy - 17, cx + 17, cy + 17,
                               fill="", outline="#a8deff", width=1)
        # Highlight glint
        self.canvas.create_oval(cx - 11, cy - 15, cx + 2, cy - 7,
                               fill=_lerp(glow, "#ffffff", 0.45), outline="")
        # Labels
        self.canvas.create_text(cx, cy + 1, text="COP",
                               fill="#ffffff", font=("Consolas", 9, "bold"))
        self.canvas.create_text(cx, cy + 13, text="AI",
                               fill=C["border_cyan"], font=("Consolas", 8, "bold"))

    def _draw_thief(self, x: int, y: int) -> None:
        left, top = self._cell_origin(x, y)
        cx = left + CELL // 2 - 3
        cy = top + CELL // 2 - 4
        pt = _pulse(self._tick, 1.5)
        glow = _lerp(C["rob_core"], C["rob_glow"], pt)
        # Glow halos
        for r, strength in ((40, 0.07), (32, 0.14), (25, 0.28)):
            hc = _lerp(C["bg"], glow, strength)
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=hc, outline="")
        # Drop shadow (diamond)
        shadow_pts = [
            cx + 3,
            cy - 24 + 4,
            cx + 24 + 3,
            cy + 4,
            cx + 3,
            cy + 24 + 4,
            cx - 24 + 3,
            cy + 4,
        ]
        self.canvas.create_polygon(shadow_pts, fill="#000000", outline="")
        # Diamond body
        pts = [cx, cy - 24, cx + 24, cy, cx, cy + 24, cx - 24, cy]
        self.canvas.create_polygon(pts, fill=glow, outline=C["text_gold"], width=2)
        # Inner diamond ring
        ri = 15
        inner_pts = [cx, cy - ri, cx + ri, cy, cx, cy + ri, cx - ri, cy]
        self.canvas.create_polygon(inner_pts, fill="", outline="#fff5c0")
        # Highlight glint
        self.canvas.create_oval(cx - 10, cy - 14, cx + 2, cy - 7,
                               fill=_lerp(glow, "#ffffff", 0.5), outline="")
        # Labels
        self.canvas.create_text(cx, cy + 2, text="ROB",
                               fill="#ffffff", font=("Consolas", 8, "bold"))
        self.canvas.create_text(cx, cy + 13, text="RUN",
                               fill=C["rob_glow"], font=("Consolas", 7, "bold"))

    def _draw_barrier(self, x: int, y: int) -> None:
        left, top = self._cell_origin(x, y)
        cx = left + CELL // 2 - 3
        cy = top + CELL // 2 - 4
        pt = _pulse(self._tick, 0.9, 0.2, 1.0)
        bc = _lerp(C["barrier_fill"], C["barrier_border"], pt)
        # Glow
        self.canvas.create_oval(cx - 24, cy - 22, cx + 24, cy + 22,
                               fill=_lerp(C["bg"], bc, 0.2), outline="")
        pts = [cx, cy - 22, cx + 20, cy + 11, cx - 20, cy + 11]
        self.canvas.create_polygon(pts, fill=bc, outline=C["barrier_border"], width=2)
        self.canvas.create_text(cx, cy + 4, text="BLOCK",
                               fill="#ffffff", font=("Consolas", 7, "bold"))

    # ── curtain intro ────────────────────────────────────────────────────────
    def _draw_curtain(self) -> None:
        w = CELL * 5 + PAD * 2
        h = CELL * 5 + BOARD_TOP + 40
        ticks_elapsed = max(0, self._curtain_end_tick - self._tick)
        ticks_total   = 16
        frac = ticks_elapsed / ticks_total           # 1→0 as curtain opens

        half = int((w / 2) * frac)
        if half > 0:
            # Left curtain panel
            self.canvas.create_rectangle(0, 0, half, h, fill="#000a14", outline="")
            # Right curtain panel
            self.canvas.create_rectangle(w - half, 0, w, h, fill="#000a14", outline="")
            # Animated edge lines
            edge_t = _pulse(self._tick, 2.0)
            edge_col = _lerp(C["border_cyan"], C["border_magenta"], edge_t)
            self.canvas.create_line(half, 0, half, h, fill=edge_col, width=3)
            self.canvas.create_line(w - half, 0, w - half, h, fill=edge_col, width=3)

        # Centre text (fade in)
        reveal = min(1.0, (ticks_total - ticks_elapsed) / 5)
        title_col = _lerp(C["bg"], C["text_gold"], reveal)
        sub_col   = _lerp(C["bg"], C["border_cyan"], reveal)
        tag_col   = _lerp(C["bg"], C["neon_green"], reveal)

        self.canvas.create_text(w / 2, h / 2 - 40, text="GAME START",
                               fill=title_col, font=("Consolas", 34, "bold"))
        self.canvas.create_text(w / 2, h / 2 + 10, text=self._players_text(),
                               fill=sub_col, font=("Consolas", 13, "bold"),
                               width=w - 120)
        self.canvas.create_text(w / 2, h / 2 + 52,
                               text="ShadowGrid Protocol Initiated",
                               fill=tag_col, font=("Consolas", 10, "bold"))

    # ── end overlay ──────────────────────────────────────────────────────────
    def _draw_end_overlay(self, winner: str) -> None:
        w = CELL * 5 + PAD * 2
        h = CELL * 5 + BOARD_TOP + 40
        cx, cy = w / 2, h / 2

        # Stippled vignette
        self.canvas.create_rectangle(0, 0, w, h, fill="#000000",
                                     stipple="gray50", outline="")
        if winner.lower() == "cop":
            box_col  = C["cop_glow"]
            win_text = "COP WINS"
            sub_text = "Target neutralised. Grid secure."
        else:
            box_col  = C["rob_glow"]
            win_text = "ROBBER WINS"
            sub_text = "Clean getaway. No trace left behind."

        # Animated glow halo
        ht = _pulse(self._tick, 1.8)
        halo_col = _lerp(C["bg"], box_col, 0.5 + ht * 0.5)
        for exp in (28, 20, 13, 6):
            self.canvas.create_rectangle(cx - 210 - exp, cy - 100 - exp,
                                         cx + 210 + exp, cy + 120 + exp,
                                         fill=_lerp(C["bg"], halo_col, 1 - exp / 32),
                                         outline="")

        self.canvas.create_rectangle(cx - 210, cy - 100, cx + 210, cy + 120,
                                     fill="#010c18", outline=box_col, width=4)

        # GAME OVER glow
        for off in (3, 2, 1):
            self.canvas.create_text(cx + off, cy - 66 + off, text="GAME OVER",
                                   fill=box_col, font=("Consolas", 32, "bold"))
        self.canvas.create_text(cx, cy - 66, text="GAME OVER",
                               fill=C["text_gold"], font=("Consolas", 32, "bold"))

        self.canvas.create_text(cx, cy - 16, text=win_text,
                               fill=box_col, font=("Consolas", 18, "bold"))
        self.canvas.create_text(cx, cy + 26, text=sub_text,
                               fill=C["text_white"], font=("Consolas", 11))
        self.canvas.create_text(cx, cy + 78,
                               text="Click Save Game to export replay",
                               fill=C["text_cyan"], font=("Consolas", 10))
        for i in range(28):
            px = 54 + (i * 47 + self._tick * 3) % max(1, w - 108)
            py = 118 + (i * 31 + self._tick * 2) % max(1, h - 236)
            pc = [C["border_cyan"], C["border_magenta"], C["border_gold"], C["neon_green"]][i % 4]
            self.canvas.create_rectangle(px, py, px + 7, py + 7, fill=pc, outline="")

    # ── status sidebar labels ────────────────────────────────────────────────
    def _update_status(self) -> None:
        actor = "Your" if self._is_human_turn() else "AI"
        moves_left = max(0, self.config.max_moves - self.state.turn_index // 2)
        self.status.config(text=f"{actor} Turn: {self.current_role.title()}")
        self.substatus.config(
            text=f"Moves left: {moves_left}   Barriers: {self.state.cop_barriers_left}")
        self.legend.config(text=(
            "Gold diamond  = Robber\n"
            "Blue circle   = Cop\n"
            "Green ring    = Legal moves\n"
            "Purple tri    = Barrier\n"
            "Right-click / B  = Place barrier"
        ))
        bstate = "normal" if self.current_role == "cop" and self._is_human_turn() else "disabled"
        self.barrier_button.config(state=bstate)

    # ── input handlers ───────────────────────────────────────────────────────
    def _click_board(self, event: tk.Event) -> None:
        if self.presentation_active or not self._is_human_turn():
            return
        cell = self._event_cell(event)
        if cell in self.highlights:
            self._apply_user_action(self.highlights[cell])

    def _right_click_board(self, event: tk.Event) -> None:
        if self.current_role == "cop" and self._is_human_turn():
            self.place_barrier()

    def _key_move(self, event: tk.Event) -> None:
        move = MOVE_KEYS.get(str(event.char).lower())
        if move:
            self.user_move(move)
        elif str(event.char).lower() == "b":
            self.place_barrier()

    def _apply_user_action(self, move: Move) -> None:
        role = self.current_role
        actor = self.state.cop if role == "cop" else self.state.thief
        clr = C["cop_glow"] if role == "cop" else C["rob_glow"]
        self._trail.append((actor.x, actor.y, clr))
        if len(self._trail) > 6:
            self._trail.pop(0)
        message = f"The human {role} is at ({actor.x},{actor.y}) and chooses {move.value}."
        self.engine.apply(self.state, Action(role, move, message))
        self.last_message[self._other(role)] = message
        self._log(f"You as {role} -> {move.value}")
        self._record_move(role, "user", move, message)
        self._record_frame(f"Human {role} moved {move.value}")
        self._after_turn()

    def _after_turn(self) -> None:
        if self._check_end():
            return
        self.current_role = self._other(self.current_role)
        self._advance_ai_if_needed()

    def _advance_ai_if_needed(self) -> None:
        if not self.finished and not self._is_human_turn():
            self.root.after(550, self.ai_turn)

    def _legal_moves(self, role: Role) -> dict[tuple[int, int], Move]:
        origin = self.state.cop if role == "cop" else self.state.thief
        legal: dict[tuple[int, int], Move] = {}
        for move in [Move.NW, Move.N, Move.NE, Move.W, Move.E, Move.SW, Move.S, Move.SE]:
            target = origin.moved(move)
            if self._is_open_for_click(target):
                legal[(target.x, target.y)] = move
        return legal

    def _sanitize_ai_action(self, action: Action) -> Action:
        if action.move == Move.BARRIER and action.role == "cop":
            return action
        fallback = self._best_ai_move(action.role)
        if action.role == "cop":
            if action.move != fallback:
                message = (
                    f"{action.message} Tactical correction: "
                    f"closing distance with {fallback.value}."
                )
                return Action(action.role, fallback, message)
            return action
        legal = set(self._legal_moves(action.role).values())
        if action.move in legal and action.move != Move.STAY:
            return action
        message = f"{action.message} I must move, so I choose {fallback.value}."
        return Action(action.role, fallback, message)

    def _best_ai_move(self, role: Role) -> Move:
        legal = self._legal_moves(role)
        if not legal:
            return Move.N
        current = self.state.cop if role == "cop" else self.state.thief
        opponent = self.state.thief if role == "cop" else self.state.cop
        ranked: list[tuple[int, int, Move]] = []
        for target_tuple, move in legal.items():
            target = Position(target_tuple[0], target_tuple[1])
            distance = target.chebyshev(opponent)
            edge_bonus = min(
                target.x,
                target.y,
                self.state.width - 1 - target.x,
                self.state.height - 1 - target.y,
            )
            if role == "cop":
                ranked.append((distance, current.chebyshev(target), move))
            else:
                ranked.append((-distance, -edge_bonus, move))
        ranked.sort()
        return ranked[0][2]

    def _is_open_for_click(self, pos: Position) -> bool:
        in_bounds = 0 <= pos.x < self.state.width and 0 <= pos.y < self.state.height
        return in_bounds and pos not in self.state.barriers

    def _is_human_turn(self) -> bool:
        mode = self.mode.get()
        return (
            mode == "cop_user_robber_user"
            or (mode == "cop_agent_robber_user" and self.current_role == "thief")
            or (mode == "cop_user_robber_agent" and self.current_role == "cop")
        )

    def _configure_agents_for_mode(self) -> None:
        if self.mode.get() == "cop_openai_robber_gemini":
            self.agents = {
                "cop":   GeminiAgent("cop",   self.config.llm, provider="openai"),
                "thief": GeminiAgent("thief", self.config.llm, provider="gemini"),
            }
        else:
            self.agents = {
                "cop":   GeminiAgent("cop",   self.config.llm),
                "thief": GeminiAgent("thief", self.config.llm),
            }

    def _check_end(self) -> bool:
        result = self.engine.result_for(self.state)
        if not result:
            return False
        self.finished = True
        self.final_result = result
        winner = "Cop" if result == "cop_wins" else "Robber"
        self._record_frame(f"Winner: {winner}")
        if result == "cop_wins":
            messagebox.showinfo(
                "ShadowGrid Alert: Capture Complete",
                "★  CASE CLOSED  ★\n\n"
                "The cop landed on the robber.\n"
                "Signals locked. Route sealed. The grid is secure.",
            )
        else:
            messagebox.showinfo(
                "ShadowGrid Alert: Legendary Escape",
                "★  CLEAN GETAWAY  ★\n\n"
                "The robber survived the full chase.\n"
                "No capture, no panic, just a beautiful escape route.",
            )
        return True

    def save_game(self) -> None:
        if not self.finished:
            messagebox.showinfo(
                "Game still running",
                "Finish the game first, then click Save Game.\n\n"
                "The exported video will stop exactly on the final board.",
            )
            return
        try:
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = export_replay_video(
                self.replay_frames,
                self.state.width,
                self.state.height,
                f"reports/shadowgrid_replay_{stamp}.mp4",
            )
            gif_path = export_replay_gif(
                self.replay_frames,
                self.state.width,
                self.state.height,
                f"reports/shadowgrid_replay_{stamp}_readme.gif",
            )
            json_path = self._save_movement_json(path, gif_path)
        except Exception as exc:
            messagebox.showerror("Could not save game", str(exc))
            return
        messagebox.showinfo(
            "Game saved",
            (
                f"Saved final game replay:\n{path.resolve()}\n\n"
                f"Saved README GIF preview:\n{gif_path.resolve()}\n\n"
                f"Saved movement JSON:\n{json_path.resolve()}"
            ),
        )

    def _record_frame(self, caption: str) -> None:
        self.replay_frames.append({"caption": caption, "state": self.engine.snapshot(self.state)})

    def _record_move(self, role: Role, actor_type: str, move: Move, message: str) -> None:
        self.movement_log.append({
            "turn": len(self.movement_log) + 1,
            "role": role,
            "actor_type": actor_type,
            "move": move.value,
            "message": message,
            "state": self.engine.snapshot(self.state),
        })

    def _save_movement_json(
        self, replay_path: Path, readme_gif_path: Path | None = None
    ) -> Path:
        path = replay_path.with_name(f"{replay_path.stem}_movements.json")
        payload = {
            "game_name": f"{GAME_NAME}: {GAME_SUBTITLE}",
            "mode": self.mode.get(),
            "players": self._players_text(),
            "result": self.final_result,
            "winner": "cop" if self.final_result == "cop_wins" else "robber",
            "grid_size": [self.state.width, self.state.height],
            "moves": self.movement_log,
            "final_state": self.engine.snapshot(self.state),
            "replay_video": str(replay_path),
            "readme_gif": str(readme_gif_path) if readme_gif_path else None,
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def _players_text(self) -> str:
        mode = self.mode.get()
        if mode == "cop_agent_robber_user":
            return "Robber: User  |  Cop: AI Agent"
        if mode == "cop_user_robber_agent":
            return "Robber: AI Agent  |  Cop: User"
        if mode == "cop_user_robber_user":
            return "Robber: User  |  Cop: User"
        return "Robber: Gemini Agent  |  Cop: OpenAI Agent"

    def _event_cell(self, event: tk.Event) -> tuple[int, int] | None:
        x = (event.x - PAD) // CELL
        y = (event.y - BOARD_TOP) // CELL
        if 0 <= x < self.state.width and 0 <= y < self.state.height:
            return int(x), int(y)
        return None

    def _cell_origin(self, x: int, y: int) -> tuple[int, int]:
        return PAD + x * CELL, BOARD_TOP + y * CELL

    def _other(self, role: Role) -> Role:
        return "cop" if role == "thief" else "thief"

    def _log(self, message: str) -> None:
        self.log.insert("end", message + "\n")
        self.log.see("end")


def main() -> None:
    PlayApp().root.mainloop()


if __name__ == "__main__":
    main()
