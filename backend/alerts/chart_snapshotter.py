"""
Headless Chart Snapshot Engine
Generates high-resolution institutional dark-mode PNG chart snapshots
with marked Entry, SL, TP1, TP2 levels, SMC zones, and Confluence HUD overlay
for instant Telegram mobile dispatch.
"""

import os
import matplotlib
matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


class ChartSnapshotter:
    DEFAULT_SNAPSHOT_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "snapshots")
    )

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or self.DEFAULT_SNAPSHOT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def render_signal_chart(
        self,
        df: pd.DataFrame,
        symbol: str,
        direction: str,
        entry_price: float,
        sl_price: float,
        tp1_price: float,
        tp2_price: float,
        confluence_score: float,
        reasons: Optional[List[str]] = None,
        obs: Optional[List[Dict[str, Any]]] = None,
        fvgs: Optional[List[Dict[str, Any]]] = None,
        file_prefix: str = "signal",
    ) -> str:
        """
        Renders an institutional candlestick chart with trade overlays and saves as high-res PNG.
        Returns the absolute filepath of the generated image.
        """
        reasons = reasons or []
        obs = obs or []
        fvgs = fvgs or []
        n_candles = min(len(df), 45)
        plot_df = df.tail(n_candles).reset_index(drop=True)

        # Chart Color Theme (Deep Institutional Dark)
        BG_COLOR = "#0D1117"
        GRID_COLOR = "#1F242C"
        TEXT_COLOR = "#C9D1D9"
        GREEN_CANDLE = "#00C853"
        RED_CANDLE = "#FF3D00"
        ENTRY_COLOR = "#2979FF"
        SL_COLOR = "#FF1744"
        TP_COLOR = "#00E676"

        fig, ax = plt.subplots(figsize=(12, 6.5), dpi=150, facecolor=BG_COLOR)
        ax.set_facecolor(BG_COLOR)

        # Plot Candlesticks
        width = 0.6
        width2 = 0.1

        for i, row in plot_df.iterrows():
            o, h, l, c = row["open"], row["high"], row["low"], row["close"]
            color = GREEN_CANDLE if c >= o else RED_CANDLE

            # High-Low Wick
            ax.plot([i, i], [l, h], color=color, linewidth=1.2, zorder=2)
            # Open-Close Body
            bottom = min(o, c)
            height = abs(c - o)
            if height == 0:
                height = 0.0001
            rect = patches.Rectangle(
                (i - width / 2, bottom),
                width,
                height,
                facecolor=color,
                edgecolor=color,
                zorder=3,
            )
            ax.add_patch(rect)

        x_max = len(plot_df) + 8  # Add padding to the right for labels

        # Draw Trade Lines
        # 1. Entry Line
        ax.axhline(entry_price, color=ENTRY_COLOR, linestyle="--", linewidth=1.5, zorder=4)
        ax.text(
            x_max - 7.5,
            entry_price,
            f" ENTRY: {entry_price:.2f}",
            color=ENTRY_COLOR,
            fontsize=9,
            weight="bold",
            va="center",
            bbox=dict(boxstyle="square,pad=0.2", facecolor=BG_COLOR, edgecolor=ENTRY_COLOR, alpha=0.8),
        )

        # 2. Stop Loss Line
        ax.axhline(sl_price, color=SL_COLOR, linestyle="--", linewidth=1.5, zorder=4)
        ax.text(
            x_max - 7.5,
            sl_price,
            f" SL: {sl_price:.2f}",
            color=SL_COLOR,
            fontsize=9,
            weight="bold",
            va="center",
            bbox=dict(boxstyle="square,pad=0.2", facecolor=BG_COLOR, edgecolor=SL_COLOR, alpha=0.8),
        )

        # 3. Take Profit 1 Line
        ax.axhline(tp1_price, color=TP_COLOR, linestyle="--", linewidth=1.5, zorder=4)
        ax.text(
            x_max - 7.5,
            tp1_price,
            f" TP1: {tp1_price:.2f} (Lock BE)",
            color=TP_COLOR,
            fontsize=9,
            weight="bold",
            va="center",
            bbox=dict(boxstyle="square,pad=0.2", facecolor=BG_COLOR, edgecolor=TP_COLOR, alpha=0.8),
        )

        # 4. Take Profit 2 Line
        ax.axhline(tp2_price, color=TP_COLOR, linestyle=":", linewidth=1.5, zorder=4)
        ax.text(
            x_max - 7.5,
            tp2_price,
            f" TP2: {tp2_price:.2f}",
            color=TP_COLOR,
            fontsize=9,
            weight="bold",
            va="center",
            bbox=dict(boxstyle="square,pad=0.2", facecolor=BG_COLOR, edgecolor=TP_COLOR, alpha=0.8),
        )

        # Draw SMC Zone Shading (Order Blocks / FVGs)
        for ob in obs:
            ob_b = ob.get("bottom", 0.0)
            ob_t = ob.get("top", 0.0)
            ob_color = "#00E676" if "BULLISH" in ob.get("type", "") else "#FF5252"
            rect = patches.Rectangle(
                (0, ob_b),
                len(plot_df),
                ob_t - ob_b,
                facecolor=ob_color,
                alpha=0.15,
                edgecolor=ob_color,
                linestyle=":",
                zorder=1,
            )
            ax.add_patch(rect)

        # Grid and Axis Styling
        ax.set_xlim(-1, x_max)
        ax.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.5, alpha=0.7)
        ax.tick_params(colors=TEXT_COLOR, labelsize=9)
        for spine in ax.spines.values():
            spine.set_color(GRID_COLOR)

        # Header Title
        now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        ax.set_title(
            f"THE LIFE CONFLUENCE TERMINAL  •  {symbol} M15  [{direction.upper()}]  •  {now_utc}",
            color=TEXT_COLOR,
            fontsize=11,
            weight="bold",
            pad=15,
            loc="left",
        )

        # Confluence HUD Badge Overlay (Top Left Card)
        grade_text = "GRADE A+" if confluence_score >= 80 else "GRADE A"
        hud_text = (
            f"[A+] SIGNAL CONFLUENCE: {confluence_score:.1f}% [{grade_text}]\n"
            f"Direction: {direction.upper()} (3-Tranche Scaling)\n"
        )
        if reasons:
            hud_text += "Key Drivers:\n" + "\n".join([f"- {r[:45]}..." if len(r) > 48 else f"- {r}" for r in reasons[:3]])

        ax.text(
            0.02,
            0.96,
            hud_text,
            transform=ax.transAxes,
            fontsize=8.5,
            color="#E6EDF3",
            va="top",
            ha="left",
            family="monospace",
            bbox=dict(
                boxstyle="round,pad=0.6",
                facecolor="#161B22",
                edgecolor="#30363D",
                alpha=0.92,
            ),
            zorder=6,
        )

        plt.tight_layout()

        # Save to file
        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{file_prefix}_{symbol}_{timestamp_str}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, facecolor=BG_COLOR, edgecolor="none", bbox_inches="tight")
        plt.close(fig)

        return filepath
