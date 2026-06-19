"""Render today's slide (cycling 0..N-1 by day count) and email it.

Usage:
    python3 send_daily_poster.py

Requires environment variables (e.g. in a .env file loaded by cron, or
exported in the shell):
    POSTER_SMTP_HOST       e.g. smtp.gmail.com
    POSTER_SMTP_PORT       e.g. 587
    POSTER_SMTP_USER       sender email address
    POSTER_SMTP_PASSWORD   app password / SMTP password
    POSTER_TO_EMAIL        recipient email address (defaults to SMTP_USER)

State (which slide is "today's") is tracked in state.json next to this file,
so the cycle advances by one slide each time this script runs (not by
calendar date), making it safe to test by re-running manually.
"""
import json
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

from pptx import Presentation

from render_slide import render_slide, PPTX_PATH

BASE_DIR = Path(__file__).parent
STATE_PATH = BASE_DIR / "state.json"
OUTPUT_DIR = BASE_DIR / "output"


def slide_count() -> int:
    return len(Presentation(str(PPTX_PATH)).slides)


def next_slide_index() -> int:
    n = slide_count()
    if STATE_PATH.exists():
        state = json.loads(STATE_PATH.read_text())
        idx = (state.get("last_index", -1) + 1) % n
    else:
        idx = 0
    STATE_PATH.write_text(json.dumps({"last_index": idx}))
    return idx


def send_email(image_path: Path, slide_index: int):
    host = os.environ["POSTER_SMTP_HOST"]
    port = int(os.environ.get("POSTER_SMTP_PORT", "587"))
    user = os.environ["POSTER_SMTP_USER"]
    password = os.environ["POSTER_SMTP_PASSWORD"]
    to_addr = os.environ.get("POSTER_TO_EMAIL", user)

    msg = EmailMessage()
    msg["Subject"] = f"Daily Graphology Poster (slide {slide_index + 1})"
    msg["From"] = user
    msg["To"] = to_addr
    msg.set_content("Today's poster is attached.")
    msg.add_attachment(
        image_path.read_bytes(),
        maintype="image",
        subtype="png",
        filename=image_path.name,
    )

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)


def main():
    idx = next_slide_index()
    out_path = OUTPUT_DIR / f"daily_poster_slide_{idx}.png"
    render_slide(idx, out_path)
    send_email(out_path, idx)
    print(f"Sent slide {idx} -> {out_path}")


if __name__ == "__main__":
    main()
