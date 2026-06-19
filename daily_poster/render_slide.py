"""Render one slide of assets/slides.pptx to a poster PNG using python-pptx + Pillow.

LibreOffice headless conversion is unavailable in this environment, so shapes
are redrawn manually: pictures are pasted, text/autoshapes are drawn with
their fill colour and centered/wrapped text.
"""
import io
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.util import Emu

BASE_DIR = Path(__file__).parent
PPTX_PATH = BASE_DIR / "assets" / "slides.pptx"
SCALE = 2  # render at 2x slide EMU->px ratio for crisper text
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def emu_to_px(emu, slide_width_emu, target_width_px):
    return int(emu * target_width_px / slide_width_emu)


def get_font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(str(FONT_DIR / name), size)


def rgb_from_color(color_format, default=(40, 40, 40)):
    try:
        if color_format.type is not None:
            rgb = color_format.rgb
            return (rgb[0], rgb[1], rgb[2])
    except (AttributeError, TypeError, KeyError):
        pass
    return default


def pick_text_color(img, box):
    x0, y0, x1, y1 = [int(v) for v in box]
    x0, y0 = max(x0, 0), max(y0, 0)
    x1, y1 = min(x1, img.width), min(y1, img.height)
    if x1 <= x0 or y1 <= y0:
        return (20, 20, 20)
    region = img.crop((x0, y0, x1, y1)).convert("L")
    avg = sum(region.getdata()) / (region.width * region.height)
    return (20, 20, 20) if avg > 140 else (255, 255, 255)


def draw_wrapped_text(draw, text, box, font, fill, align="left"):
    x0, y0, x1, y1 = box
    max_width = x1 - x0
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        line = ""
        for word in words:
            trial = (line + " " + word).strip()
            if draw.textlength(trial, font=font) <= max_width or not line:
                line = trial
            else:
                lines.append(line)
                line = word
        lines.append(line)

    line_height = font.size + 6
    y = y0
    for line in lines:
        if y + line_height > y1:
            break
        w = draw.textlength(line, font=font)
        x = x0
        if align == "center":
            x = x0 + (max_width - w) / 2
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height


def render_slide(slide_index: int, out_path: Path):
    prs = Presentation(str(PPTX_PATH))
    slide = prs.slides[slide_index]
    sw_emu, sh_emu = prs.slide_width, prs.slide_height

    target_w = 1600
    target_h = int(target_w * sh_emu / sw_emu)
    img = Image.new("RGB", (target_w, target_h), "white")
    draw = ImageDraw.Draw(img)

    def to_px(shape_attr, dim):
        emu = getattr(shape, shape_attr, None)
        if emu is None:
            return 0
        return emu_to_px(emu, sw_emu if dim == "w" else sh_emu, target_w if dim == "w" else target_h)

    for shape in slide.shapes:
        try:
            left = emu_to_px(shape.left or 0, sw_emu, target_w)
            top = emu_to_px(shape.top or 0, sh_emu, target_h)
            width = emu_to_px(shape.width or 0, sw_emu, target_w)
            height = emu_to_px(shape.height or 0, sh_emu, target_h)
        except TypeError:
            continue

        if shape.shape_type == 13:  # PICTURE
            try:
                blob = shape.image.blob
                pic = Image.open(io.BytesIO(blob)).convert("RGB")
                pic = pic.resize((max(width, 1), max(height, 1)))
                img.paste(pic, (left, top))
            except Exception:
                pass
            continue

        fill_rgb = None
        try:
            if shape.fill.type is not None:
                fill_rgb = rgb_from_color(shape.fill.fore_color, default=None)
        except Exception:
            fill_rgb = None
        if fill_rgb:
            draw.rectangle([left, top, left + width, top + height], fill=fill_rgb)

        if getattr(shape, "has_text_frame", False) and shape.text_frame.text.strip():
            text = shape.text_frame.text.strip()
            is_title = "title" in (shape.name or "").lower() or (
                shape.shape_type == 14 and len(text) < 60 and slide.shapes[0] is not shape
            )
            font_size = 34 if is_title else 20
            font = get_font(font_size, bold=is_title)
            pad = 10
            text_box = (left + pad, top + pad, left + width - pad, top + height - pad)
            text_color = fill_rgb and pick_text_color(img, (left, top, left + width, top + height)) or pick_text_color(img, text_box)
            draw_wrapped_text(
                draw,
                text,
                text_box,
                font,
                fill=text_color,
                align="center" if is_title else "left",
            )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG")
    return out_path


if __name__ == "__main__":
    idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else BASE_DIR / "output" / f"slide_{idx}.png"
    render_slide(idx, out)
    print(f"Rendered slide {idx} -> {out}")
