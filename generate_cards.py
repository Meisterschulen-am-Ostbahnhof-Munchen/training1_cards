"""Automated Training Card Generator for 4diac Exercises.

Generates 7cm x 9cm portrait training cards from 4diac .SUB exercise files,
matching the logiBUS Mini-Trainer hardware overlay layout and rendering logic
blocks in the IEC 61499 SVG style using the narrow, engineering TGL font.
"""

import os
import sys
import re
import glob
import base64
import argparse
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

# Add path to IEC61499_FunctionBlock_SVG renderer
SVG_LIB_PATH = r"C:\git\fh\IEC61499_FunctionBlock_SVG"
if SVG_LIB_PATH not in sys.path and os.path.exists(SVG_LIB_PATH):
    sys.path.append(SVG_LIB_PATH)

from iec61499_network_to_svg import (
    NetworkParser, TypeResolver, NetworkSVGRenderer, NetworkLayoutEngine,
    load_block_size_settings, FBInstance, Connection, NetworkModel,
    _xml_escape
)

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import svglib.svglib as svglib
from reportlab.graphics import renderPDF

# Card geometry: 7.0 cm x 9.0 cm (Hochformat / Portrait)
# 1 cm = 50 SVG units (Card is 350 x 450 units)
CARD_W_MM = 70.0
CARD_H_MM = 90.0
SVG_W = 350.0
SVG_H = 450.0
UNITS_PER_CM = 50.0

DEFAULT_EXERCISE = r"C:\git\ms-docs\4diac_training1\Ventilsteuerung\4diacIDE-workspace\test_AX\Uebungen\Uebung_002a_AX.SUB"
DEFAULT_EXERCISES_DIR = r"C:\git\ms-docs\4diac_training1\Ventilsteuerung\4diacIDE-workspace\test_AX\Uebungen"
DEFAULT_TYPE_LIBS = [
    r"C:\git\ms-docs\4diac_training1\Ventilsteuerung\4diacIDE-workspace\.lib"
]

TGL_17_PATH = r"C:\git\fh\IEC61499_FunctionBlock_SVG\tgl\TGL 0-17_std.ttf"
TGL_16_PATH = r"C:\git\fh\IEC61499_FunctionBlock_SVG\tgl\TGL 0-16_std.ttf"


def init_tgl_fonts():
    """Registers TGL fonts in ReportLab and svglib."""
    if os.path.exists(TGL_17_PATH):
        try:
            pdfmetrics.registerFont(TTFont("TGL 0-17_std", TGL_17_PATH))
            pdfmetrics.registerFont(TTFont("TGL 0-17", TGL_17_PATH))
            svglib.register_font("TGL 0-17_std", TGL_17_PATH)
            svglib.register_font("TGL 0-17", TGL_17_PATH)
        except Exception:
            pass

    if os.path.exists(TGL_16_PATH):
        try:
            pdfmetrics.registerFont(TTFont("TGL 0-16_std", TGL_16_PATH))
            pdfmetrics.registerFont(TTFont("TGL 0-16", TGL_16_PATH))
            svglib.register_font("TGL 0-16_std", TGL_16_PATH)
            svglib.register_font("TGL 0-16", TGL_16_PATH)
        except Exception:
            pass


init_tgl_fonts()


def get_embedded_font_style() -> str:
    """Generates an SVG <style> tag embedding the TGL font files as base64 Data URIs."""
    parts = ["  <style>"]
    if os.path.exists(TGL_17_PATH):
        try:
            with open(TGL_17_PATH, "rb") as f:
                b64_17 = base64.b64encode(f.read()).decode("ascii")
            parts.append(f'''    @font-face {{
      font-family: "TGL 0-17_std";
      src: url("data:font/truetype;charset=utf-8;base64,{b64_17}") format("truetype");
      font-style: normal;
      font-weight: normal;
    }}
    @font-face {{
      font-family: "TGL 0-17";
      src: url("data:font/truetype;charset=utf-8;base64,{b64_17}") format("truetype");
      font-style: normal;
      font-weight: normal;
    }}''')
        except Exception:
            pass

    if os.path.exists(TGL_16_PATH):
        try:
            with open(TGL_16_PATH, "rb") as f:
                b64_16 = base64.b64encode(f.read()).decode("ascii")
            parts.append(f'''    @font-face {{
      font-family: "TGL 0-16_std";
      src: url("data:font/truetype;charset=utf-8;base64,{b64_16}") format("truetype");
      font-style: normal;
      font-weight: normal;
    }}
    @font-face {{
      font-family: "TGL 0-16";
      src: url("data:font/truetype;charset=utf-8;base64,{b64_16}") format("truetype");
      font-style: normal;
      font-weight: normal;
    }}''')
        except Exception:
            pass

    parts.append("  </style>")
    return "\n".join(parts)


def identify_io_pin(instance: FBInstance) -> Optional[str]:
    """Determines whether an instance represents a hardware IO terminal (I1..I8, Q1..Q8, AI1..AI3).

    Returns the pin name (e.g. 'I1', 'Q2', 'AI1') or None if it is a logic block.
    """
    name = instance.name
    type_name = instance.type_name
    params = instance.parameters

    # Check Input parameter
    input_param = params.get("Input", "")
    m = re.match(r"^Input_I(\d+)$", input_param)
    if m:
        return f"I{m.group(1)}"

    # Check Output parameter
    output_param = params.get("Output", "")
    m = re.match(r"^Output_Q(\d+)$", output_param)
    if m:
        return f"Q{m.group(1)}"

    # Check instance name patterns
    m = re.search(r"DigitalInput_I(\d+)", name, re.IGNORECASE)
    if m:
        return f"I{m.group(1)}"

    m = re.search(r"DigitalOutput_Q(\d+)", name, re.IGNORECASE)
    if m:
        return f"Q{m.group(1)}"

    m = re.search(r"AnalogInput_I?(\d+)", name, re.IGNORECASE)
    if m:
        return f"AI{m.group(1)}"

    m = re.search(r"AnalogInput_AI(\d+)", name, re.IGNORECASE)
    if m:
        return f"AI{m.group(1)}"

    # Check type patterns
    if "logiBUS::io::DI::" in type_name and name.startswith("I"):
        return name
    if "logiBUS::io::DQ::" in type_name and name.startswith("Q"):
        return name

    return None


@dataclass
class TerminalPin:
    name: str
    direction: str  # 'input' or 'output'
    x: float
    y: float
    port_side: str  # 'left' or 'right'


def get_pin_positions() -> Dict[str, TerminalPin]:
    """Returns the positions of all pins on the 350x450 card."""
    pins = {}

    # Digital Inputs I1 to I8 along left margin
    # Located at 1.0, 2.0, ..., 8.0 cm from top (50, 100, ..., 400)
    for i in range(1, 9):
        pin_name = f"I{i}"
        py = i * UNITS_PER_CM
        pins[pin_name] = TerminalPin(
            name=pin_name,
            direction="input",
            x=0.0,
            y=py,
            port_side="left"
        )

    # Digital Outputs Q1 to Q8 along right margin
    for i in range(1, 9):
        pin_name = f"Q{i}"
        py = i * UNITS_PER_CM
        pins[pin_name] = TerminalPin(
            name=pin_name,
            direction="output",
            x=SVG_W,
            y=py,
            port_side="right"
        )

    return pins


def wrap_text(text: str, max_chars: int = 55) -> List[str]:
    """Simple greedy word wrapper."""
    words = text.split()
    lines = []
    curr = []
    curr_len = 0
    for w in words:
        if curr_len + len(w) + (1 if curr else 0) <= max_chars:
            curr.append(w)
            curr_len += len(w) + (1 if len(curr) > 1 else 0)
        else:
            if curr:
                lines.append(" ".join(curr))
            curr = [w]
            curr_len = len(w)
    if curr:
        lines.append(" ".join(curr))
    return lines


def generate_card_svg(subapp_file: str, type_libs: Optional[List[str]] = None) -> str:
    """Parses a .SUB file and generates a complete 70mm x 90mm SVG training card."""
    if type_libs is None:
        type_libs = list(DEFAULT_TYPE_LIBS)

    # Add the folder containing the .SUB file
    sub_dir = os.path.dirname(os.path.abspath(subapp_file))
    if sub_dir not in type_libs:
        type_libs.append(sub_dir)

    # 1. Parse and resolve types
    parser = NetworkParser()
    model = parser.parse(subapp_file)
    resolver = TypeResolver(type_libs)
    resolver.resolve(model)

    # 2. Standard layout engine to get accurate FB sizes and internal port positions
    settings = load_block_size_settings()
    layout_engine = NetworkLayoutEngine(settings=settings)
    layout_engine.layout(model)
    renderer = NetworkSVGRenderer(show_shadow=True, show_grid=False, settings=settings)

    # 3. Classify instances into IO pins and Logic blocks
    io_map = {}  # instance_name -> pin_name (e.g. 'DigitalInput_I1' -> 'I1')
    logic_instances = []

    for inst in model.instances:
        pin = identify_io_pin(inst)
        if pin:
            io_map[inst.name] = pin
        else:
            logic_instances.append(inst)

    pins = get_pin_positions()

    # 4. Map connections and find active pins
    card_connections = []
    active_pins = set()

    for conn in model.connections:
        src_parts = conn.source.split(".")
        dst_parts = conn.destination.split(".")
        src_inst = src_parts[0]
        dst_inst = dst_parts[0]

        source_pin = io_map.get(src_inst)
        dest_pin = io_map.get(dst_inst)

        if source_pin:
            active_pins.add(source_pin)
        if dest_pin:
            active_pins.add(dest_pin)

        card_connections.append({
            "conn": conn,
            "source_pin": source_pin,
            "source_inst": None if source_pin else src_inst,
            "source_port": src_parts[1] if len(src_parts) > 1 else "",
            "dest_pin": dest_pin,
            "dest_inst": None if dest_pin else dst_inst,
            "dest_port": dst_parts[1] if len(dst_parts) > 1 else ""
        })

    # 5. Position logic blocks inside the card area
    # Badges sit at x=0..16 on left, x=334..350 on right.
    # Safe horizontal range for logic blocks: [35.0, 315.0]
    # Safe vertical range for logic blocks: [30.0, 395.0]
    if len(logic_instances) == 1:
        # Single block (like AX_AND_2 in Uebung_002a_AX)
        inst = logic_instances[0]
        # Centered horizontally
        inst.render_x = (SVG_W - inst.block_width) / 2.0

        # Vertically: find connected input pins
        connected_input_y = []
        for cinfo in card_connections:
            if cinfo["source_pin"] and cinfo["source_pin"] in pins:
                connected_input_y.append(pins[cinfo["source_pin"]].y)

        if connected_input_y:
            target_mid_y = sum(connected_input_y) / len(connected_input_y)
        else:
            target_mid_y = 1.5 * UNITS_PER_CM

        # Center the block's input ports around target_mid_y
        inst.render_y = target_mid_y - inst.block_height / 2.0
        # Ensure block stays within safe margins
        inst.render_y = max(30.0, min(inst.render_y, 395.0 - inst.block_height))

    elif len(logic_instances) > 1:
        # Multiple blocks: scale their original 4diac coordinates into the card's safe interior area
        min_4d_x = min(inst.x for inst in logic_instances)
        max_4d_x = max(inst.x for inst in logic_instances)
        min_4d_y = min(inst.y for inst in logic_instances)
        max_4d_y = max(inst.y for inst in logic_instances)

        span_4d_x = max(1.0, max_4d_x - min_4d_x)
        span_4d_y = max(1.0, max_4d_y - min_4d_y)

        x_safe_min = 40.0
        x_safe_max = 310.0
        y_safe_min = 35.0
        y_safe_max = 395.0

        for inst in logic_instances:
            norm_x = (inst.x - min_4d_x) / span_4d_x if span_4d_x > 0 else 0.5
            norm_y = (inst.y - min_4d_y) / span_4d_y if span_4d_y > 0 else 0.5

            inst_avail_w = max(0.0, (x_safe_max - x_safe_min) - inst.block_width)
            inst_avail_h = max(0.0, (y_safe_max - y_safe_min) - inst.block_height)

            inst.render_x = x_safe_min + norm_x * inst_avail_w
            inst.render_y = y_safe_min + norm_y * inst_avail_h

    # Recompute port positions on the placed logic instances
    instance_map = {}
    for inst in logic_instances:
        instance_map[inst.name] = inst
        inst.port_positions = {}
        # Event inputs
        y = inst.render_y + 2 + renderer.PORT_ROW_HEIGHT / 2
        for port in inst.event_inputs:
            inst.port_positions[port.name] = (inst.render_x, y)
            y += renderer.PORT_ROW_HEIGHT
        # Event outputs
        y = inst.render_y + 2 + renderer.PORT_ROW_HEIGHT / 2
        for port in inst.event_outputs:
            inst.port_positions[port.name] = (inst.render_x + inst.block_width, y)
            y += renderer.PORT_ROW_HEIGHT
        # Data inputs
        y = inst.render_y + inst.name_section_bottom + 2 + renderer.PORT_ROW_HEIGHT / 2
        for port in inst.data_inputs:
            inst.port_positions[port.name] = (inst.render_x, y)
            y += renderer.PORT_ROW_HEIGHT
        # Data outputs
        y = inst.render_y + inst.name_section_bottom + 2 + renderer.PORT_ROW_HEIGHT / 2
        for port in inst.data_outputs:
            inst.port_positions[port.name] = (inst.render_x + inst.block_width, y)
            y += renderer.PORT_ROW_HEIGHT
        # Sockets (adapter inputs)
        y = inst.render_y + inst.adapter_section_top + 2 + renderer.PORT_ROW_HEIGHT / 2
        for port in inst.sockets:
            inst.port_positions[port.name] = (inst.render_x, y)
            y += renderer.PORT_ROW_HEIGHT
        # Plugs (adapter outputs)
        y = inst.render_y + inst.adapter_section_top + 2 + renderer.PORT_ROW_HEIGHT / 2
        for port in inst.plugs:
            inst.port_positions[port.name] = (inst.render_x + inst.block_width, y)
            y += renderer.PORT_ROW_HEIGHT

    # 6. Build SVG content
    svg = []
    svg.append('<svg xmlns="http://www.w3.org/2000/svg"')
    svg.append(f'     viewBox="0 0 {SVG_W} {SVG_H}"')
    svg.append(f'     width="{CARD_W_MM}mm" height="{CARD_H_MM}mm">')

    # Embedded TGL Font Style
    svg.append(get_embedded_font_style())

    # Drop shadow filter
    svg.append('''  <defs>
    <filter id="dropShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="2" result="blur"/>
      <feOffset in="blur" dx="1" dy="1" result="offsetBlur"/>
      <feFlood flood-color="#000000" flood-opacity="0.35" result="shadowColor"/>
      <feComposite in="shadowColor" in2="offsetBlur" operator="in" result="shadow"/>
      <feMerge>
        <feMergeNode in="shadow"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>''')

    # Base card background (White)
    svg.append(f'  <rect x="0" y="0" width="{SVG_W}" height="{SVG_H}" fill="white"/>')

    # Outer border (cut boundary)
    svg.append(f'  <rect x="0.5" y="0.5" width="{SVG_W-1}" height="{SVG_H-1}" fill="none" stroke="#BDC3C7" stroke-width="1"/>')

    # Subtle 1cm grid
    for i in range(1, 7):
        gx = i * UNITS_PER_CM
        svg.append(f'  <line x1="{gx}" y1="0" x2="{gx}" y2="{SVG_H}" stroke="#F5F7F8" stroke-width="0.8"/>')
    for j in range(1, 9):
        gy = j * UNITS_PER_CM
        svg.append(f'  <line x1="0" y1="{gy}" x2="{SVG_W}" y2="{gy}" stroke="#F5F7F8" stroke-width="0.8"/>')

    # Connections group (rendered behind blocks)
    svg.append('  <g id="connections">')
    for cinfo in card_connections:
        conn = cinfo["conn"]
        src_pt = None
        dst_pt = None

        if cinfo["source_pin"] and cinfo["source_pin"] in pins:
            pin = pins[cinfo["source_pin"]]
            # Connect right from the apex of the semicircle badge on the left
            src_pt = (15.0, pin.y)
        elif cinfo["source_inst"] in instance_map:
            inst = instance_map[cinfo["source_inst"]]
            src_pt = inst.port_positions.get(cinfo["source_port"])

        if cinfo["dest_pin"] and cinfo["dest_pin"] in pins:
            pin = pins[cinfo["dest_pin"]]
            # Connect directly to the apex of the semicircle badge on the right
            dst_pt = (SVG_W - 15.0, pin.y)
        elif cinfo["dest_inst"] in instance_map:
            inst = instance_map[cinfo["dest_inst"]]
            dst_pt = inst.port_positions.get(cinfo["dest_port"])

        if src_pt and dst_pt:
            sx, sy = src_pt
            dx, dy = dst_pt

            if abs(sy - dy) < 2.0:
                waypoints = [src_pt, dst_pt]
            else:
                mid_x = (sx + dx) / 2.0
                if cinfo["source_pin"]:
                    mid_x = sx + 30.0
                elif cinfo["dest_pin"]:
                    mid_x = dx - 30.0

                waypoints = [
                    (sx, sy),
                    (mid_x, sy),
                    (mid_x, dy),
                    (dx, dy)
                ]

            color = renderer._get_connection_color(conn, model, instance_map)
            is_double = renderer._is_double_line_connection(conn, model, instance_map)
            svg.append(renderer._render_connection(waypoints, color, double_line=is_double))

    svg.append('  </g>')

    # Render logic FB instances
    svg.append('  <g id="instances">')
    for inst in logic_instances:
        svg.append(renderer._render_instance(inst))
    svg.append('  </g>')

    # Render only the pins used in the exercise, right at the border (semicircles)
    # Left margin pins: I1 to I8 (only if used!)
    for i in range(1, 9):
        pin_name = f"I{i}"
        if pin_name not in active_pins:
            continue
        py = i * UNITS_PER_CM
        # Semicircle / half-pill directly at x = 0 (radius = 13.5, height = 27, depth = 15)
        svg.append(f'  <path d="M 0,{py-13.5:.1f} L 2,{py-13.5:.1f} A 13.5,13.5 0 0,1 2,{py+13.5:.1f} L 0,{py+13.5:.1f} Z" fill="#FFFFFF" stroke="#2C3E50" stroke-width="1.2"/>')
        # Center marker (+)
        svg.append(f'  <line x1="12" y1="{py}" x2="15" y2="{py}" stroke="#BDC3C7" stroke-width="0.6"/>')
        # Label in TGL font
        svg.append(f'  <text x="7" y="{py+3.5:.1f}" font-family="\'TGL 0-17_std\', \'TGL 0-17\', Helvetica, Arial, sans-serif" font-size="9.5" font-weight="bold" fill="#2C3E50" text-anchor="middle">{pin_name}</text>')

    # Right margin pins: Q1 to Q8 (only if used!)
    for i in range(1, 9):
        pin_name = f"Q{i}"
        if pin_name not in active_pins:
            continue
        py = i * UNITS_PER_CM
        # Semicircle / half-pill directly at x = SVG_W (350)
        svg.append(f'  <path d="M {SVG_W},{py-13.5:.1f} L {SVG_W-2},{py-13.5:.1f} A 13.5,13.5 0 0,0 {SVG_W-2},{py+13.5:.1f} L {SVG_W},{py+13.5:.1f} Z" fill="#FFFFFF" stroke="#2C3E50" stroke-width="1.2"/>')
        # Center marker (+)
        svg.append(f'  <line x1="{SVG_W-15}" y1="{py}" x2="{SVG_W-12}" y2="{py}" stroke="#BDC3C7" stroke-width="0.6"/>')
        # Label in TGL font
        svg.append(f'  <text x="{SVG_W-7}" y="{py+3.5:.1f}" font-family="\'TGL 0-17_std\', \'TGL 0-17\', Helvetica, Arial, sans-serif" font-size="9.5" font-weight="bold" fill="#2C3E50" text-anchor="middle">{pin_name}</text>')

    # Bottom Center: Exercise Name, Line Break, Full-width Description
    ex_name = model.name or os.path.splitext(os.path.basename(subapp_file))[0]
    comment = model.comment or ""

    # Exercise Name (bold, centered, font-size 10.5 pt)
    svg.append(f'  <text x="175" y="415" font-family="\'TGL 0-17_std\', \'TGL 0-17\', Helvetica, Arial, sans-serif" font-size="10.5" font-weight="bold" fill="#2C3E50" text-anchor="middle">{_xml_escape(ex_name)}</text>')

    # Description (wrapped across the full 7cm width, centered, font-size 7.5 pt)
    if comment:
        desc_lines = wrap_text(comment, max_chars=52)
        desc_y = 428.0
        for dline in desc_lines[:3]:
            svg.append(f'  <text x="175" y="{desc_y:.1f}" font-family="\'TGL 0-17_std\', \'TGL 0-17\', Helvetica, Arial, sans-serif" font-size="7.5" fill="#566573" text-anchor="middle">{_xml_escape(dline)}</text>')
            desc_y += 10.0

    svg.append('</svg>')
    return "\n".join(svg)


def draw_crop_marks(c: canvas.Canvas, x: float, y: float, w: float, h: float, length: float = 6 * mm, offset: float = 2 * mm):
    """Draws cutting crop marks around the card boundary."""
    c.setStrokeColor(colors.HexColor('#7F8C8D'))
    c.setLineWidth(0.4)

    # Bottom-Left
    c.line(x - offset - length, y, x - offset, y)
    c.line(x, y - offset - length, x, y - offset)

    # Bottom-Right
    c.line(x + w + offset, y, x + w + offset + length, y)
    c.line(x + w, y - offset - length, x + w, y - offset)

    # Top-Left
    c.line(x - offset - length, y + h, x - offset, y + h)
    c.line(x, y + h + offset, x, y + h + offset + length)

    # Top-Right
    c.line(x + w + offset, y + h, x + w + offset + length, y + h)
    c.line(x + w, y + h + offset, x + w, y + h + offset + length)


def render_card_on_pdf(c: canvas.Canvas, svg_content: str, x: float, y: float, w: float = 7.0 * cm, h: float = 9.0 * cm):
    """Draws an SVG training card at the specified position on the ReportLab canvas."""
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False, mode="w", encoding="utf-8") as tf:
        tf.write(svg_content)
        temp_path = tf.name

    try:
        drawing = svglib.svg2rlg(temp_path)
        if drawing:
            scale_x = w / drawing.width
            scale_y = h / drawing.height
            drawing.width = w
            drawing.height = h
            drawing.scale(scale_x, scale_y)
            renderPDF.draw(drawing, c, x, y)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def generate_single_card_pdf(subapp_file: str, output_pdf: str = "logiBUS_single_card.pdf"):
    """Generates a single-card PDF page centered on A4 with crop marks."""
    svg_content = generate_card_svg(subapp_file)
    c = canvas.Canvas(output_pdf, pagesize=A4)
    page_w, page_h = A4

    card_w = 7.0 * cm
    card_h = 9.0 * cm

    x = (page_w - card_w) / 2.0
    y = (page_h - card_h) / 2.0

    # Header title outside card
    c.setFillColor(colors.HexColor('#2C3E50'))
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(page_w / 2.0, page_h - 2.5 * cm, "logiBUS\u00ae Mini-Trainer - Trainingskarte")
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor('#7F8C8D'))
    c.drawCentredString(page_w / 2.0, page_h - 3.0 * cm, "Kartengr\u00f6\u00dfe: 7,0 cm x 9,0 cm (Hochformat). Bitte an den Schnittmarken ausschneiden.")

    # Render card
    render_card_on_pdf(c, svg_content, x, y, card_w, card_h)

    # Crop marks
    draw_crop_marks(c, x, y, card_w, card_h)

    # Exercise description at bottom of page
    parser = NetworkParser()
    model = parser.parse(subapp_file)
    ex_name = model.name or os.path.splitext(os.path.basename(subapp_file))[0]
    comment = model.comment or ""

    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor('#2C3E50'))
    c.drawCentredString(page_w / 2.0, 3.5 * cm, f"\u00dcbung: {ex_name}")

    if comment:
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor('#566573'))
        c.drawCentredString(page_w / 2.0, 3.0 * cm, comment)

    c.showPage()
    c.save()
    print(f"Generated single card PDF: {output_pdf}")


def generate_multi_cards_pdf(subapp_files: List[str], output_pdf: str = "logiBUS_multi_cards.pdf"):
    """Generates a multi-card PDF with a 2x3 grid (6 cards per A4 page) for easy printing and cutting."""
    c = canvas.Canvas(output_pdf, pagesize=A4)
    page_w, page_h = A4

    card_w = 7.0 * cm
    card_h = 9.0 * cm

    cols = 2
    rows = 3
    cards_per_page = cols * rows

    grid_w = cols * card_w
    grid_h = rows * card_h

    start_x = (page_w - grid_w) / 2.0
    start_y = (page_h - grid_h) / 2.0

    num_pages = (len(subapp_files) + cards_per_page - 1) // cards_per_page

    for page_idx in range(num_pages):
        draw_crop_marks(c, start_x, start_y, grid_w, grid_h, length=8 * mm, offset=3 * mm)

        for slot in range(cards_per_page):
            idx = page_idx * cards_per_page + slot
            if idx >= len(subapp_files):
                break

            sub_file = subapp_files[idx]
            col = slot % cols
            row = slot // cols
            grid_row = (rows - 1) - row

            x = start_x + col * card_w
            y = start_y + grid_row * card_h

            svg_content = generate_card_svg(sub_file)
            render_card_on_pdf(c, svg_content, x, y, card_w, card_h)

            draw_crop_marks(c, x, y, card_w, card_h, length=4 * mm, offset=1.5 * mm)

        c.showPage()

    c.save()
    print(f"Generated multi card PDF: {output_pdf}")


def main():
    arg_parser = argparse.ArgumentParser(description="Generate 7x9cm portrait training cards from 4diac exercises.")
    arg_parser.add_argument("--sub", type=str, default=DEFAULT_EXERCISE, help="Path to .SUB exercise file")
    arg_parser.add_argument("--all", action="store_true", help="Generate multi-card PDF for all exercises in folder")
    arg_parser.add_argument("--folder", type=str, default=DEFAULT_EXERCISES_DIR, help="Folder containing .SUB files")
    arg_parser.add_argument("--single-out", type=str, default="logiBUS_single_card.pdf", help="Output path for single card PDF")
    arg_parser.add_argument("--multi-out", type=str, default="logiBUS_multi_cards.pdf", help="Output path for multi card PDF")
    args = arg_parser.parse_args()

    if args.all:
        files = sorted(glob.glob(os.path.join(args.folder, "*.SUB")))
        print(f"Found {len(files)} exercises in {args.folder}")
        generate_multi_cards_pdf(files, args.multi_out)
        if files:
            generate_single_card_pdf(files[0], args.single_out)
    else:
        target_sub = args.sub
        if not os.path.isabs(target_sub) and not os.path.exists(target_sub):
            candidate = os.path.join(args.folder, target_sub)
            if os.path.exists(candidate):
                target_sub = candidate

        print(f"Processing exercise: {target_sub}")
        base_name = os.path.splitext(os.path.basename(target_sub))[0]
        svg_out = f"{base_name}_card.svg"
        svg_content = generate_card_svg(target_sub)
        with open(svg_out, "w", encoding="utf-8") as f:
            f.write(svg_content)
        print(f"Saved SVG: {svg_out}")

        generate_single_card_pdf(target_sub, args.single_out)

        multi_list = [target_sub] * 6
        generate_multi_cards_pdf(multi_list, args.multi_out)

    print("Generation complete!")


if __name__ == "__main__":
    main()
