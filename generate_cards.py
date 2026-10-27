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
import itertools
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Set

# Add path to IEC61499_FunctionBlock_SVG renderer
SVG_LIB_PATH = r"/home/moritz/Git-Repos/IEC61499_FunctionBlock_SVG"
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
# Blocks are drawn 4 % smaller so that the port rows fit the 1 cm pin grid (52 -> 50 units between REQ and CD)
BLOCK_SCALE = 0.96
# Vertical clearance between stacked blocks: room for the instance name drawn above the lower block
BLOCK_LABEL_GAP = 26.0

# DEFAULT_EXERCISE = r"C:\git\ms-docs\4diac_training1\Ventilsteuerung\4diacIDE-workspace\test_AX\Uebungen\Uebung_002a_AX.SUB"
# DEFAULT_EXERCISES_DIRS = [
#     r"C:\git\ms-docs\4diac_training1\Ventilsteuerung\4diacIDE-workspace\test_AX",
#     r"C:\git\ms-docs\4diac_training1\Ventilsteuerung\4diacIDE-workspace\test_B",
# ]
# DEFAULT_EXERCISES_DIR = DEFAULT_EXERCISES_DIRS[0]
# DEFAULT_TYPE_LIBS = [
#     r"C:\git\ms-docs\4diac_training1\Ventilsteuerung\4diacIDE-workspace\.lib",
#     r"C:\git\ms-docs\4diac_training1\Ventilsteuerung\4diacIDE-workspace\test_AX",
#     r"C:\git\ms-docs\4diac_training1\Ventilsteuerung\4diacIDE-workspace\test_B",
# ]

DEFAULT_EXERCISE = r"/home/moritz/Git-Repos/4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX/Uebungen/Uebung_002a_AX.SUB"
DEFAULT_EXERCISES_DIRS = [
    r"/home/moritz/Git-Repos/4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX",
    r"/home/moritz/Git-Repos/4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_B",
]
DEFAULT_EXERCISES_DIR = DEFAULT_EXERCISES_DIRS[0]
DEFAULT_TYPE_LIBS = [
    r"/home/moritz/Git-Repos/4diac_training1/Ventilsteuerung/4diacIDE-workspace/.lib",
    r"/home/moritz/Git-Repos/4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_AX",
    r"/home/moritz/Git-Repos/4diac_training1/Ventilsteuerung/4diacIDE-workspace/test_B",
]

_FONTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
TGL_17_PATH = os.path.join(_FONTS_DIR, "TGL 0-17.ttf")
TGL_16_PATH = os.path.join(_FONTS_DIR, "TGL 0-16.ttf")

EVENT_LABELS = {
    "BUTTON_SINGLE_CLICK": "Klicken",
    "BUTTON_LONG_PRESS_START": "drücken",
    "BUTTON_LONG_PRESS_UP": "Loslassen",
    "BUTTON_LONG_PRESS_HOLD": "Halten",
    "BUTTON_PRESS_DOWN": "drücken",
    "BUTTON_PRESS_END": "Loslassen",
    "BUTTON_DOUBLE_CLICK": "Doppelklick",
    "BUTTON_MULTIPLE_CLICK": "Mehrfachklick",
    "SK_PRESSED": "Gedrückt",
    "SK_RELEASED": "Losgelassen",
    "BT_PRESSED_LATCHED": "Rastend Ein",
    "BT_RELEASED_UNLATCHED": "Rastend Aus",
}


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


def identify_passthrough(instance: FBInstance) -> Optional[Tuple[str, str, str]]:
    """Identifies pass-through instances (e.g. logiBUS_IXA_TO_logiBUS_QXA, logiBUS_IX_TO_logiBUS_QX).

    Returns (input_pin, output_pin, conn_type) or None.
    """
    params = instance.parameters
    in_val = params.get("Input", "")
    out_val = params.get("Output", "")

    m_in = re.search(r"Input_I(\d+)", in_val, re.IGNORECASE) or re.search(r"^I(\d+)$", in_val)
    m_out = re.search(r"Output_Q(\d+)", out_val, re.IGNORECASE) or re.search(r"^Q(\d+)$", out_val)

    if m_in and m_out:
        in_pin = f"I{m_in.group(1)}"
        out_pin = f"Q{m_out.group(1)}"
        conn_type = "adapter" if ("IXA" in instance.type_name or "QXA" in instance.type_name or "AX" in instance.type_name) else "data"
        return in_pin, out_pin, conn_type

    if "TO_logiBUS" in instance.type_name or "TO_" in instance.type_name:
        m_in = re.search(r"I(\d+)", in_val) or re.search(r"I(\d+)", instance.name)
        m_out = re.search(r"Q(\d+)", out_val) or re.search(r"Q(\d+)", instance.name)
        if m_in and m_out:
            in_pin = f"I{m_in.group(1)}"
            out_pin = f"Q{m_out.group(1)}"
            conn_type = "adapter" if ("IXA" in instance.type_name or "AX" in instance.type_name) else "data"
            return in_pin, out_pin, conn_type

    return None


def identify_io_pin(instance: FBInstance) -> Optional[str]:
    """Determines whether an instance represents a hardware IO terminal (I1..I8, Q1..Q8, AI1..AI3).

    Returns the pin name (e.g. 'I1', 'Q2', 'AI1') or None if it is a logic block.
    """
    # If instance is a pass-through block connecting both input and output, it's not a single terminal
    if identify_passthrough(instance):
        return None

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


class PinNo(float):
    """Pin number used for ordering; Q56 is the extra output between Q5 and Q6 (sorts as 5.5, prints as 56)."""

    def __new__(cls, num: int):
        obj = super().__new__(cls, 5.5 if num == 56 else num)
        obj.label = num
        return obj

    def __str__(self):
        return str(self.label)

    __repr__ = __str__


def pin_slot(pin_name: str) -> float:
    """Returns the card slot (1..8, Q56 = 5.5) of a pin name such as 'I3', 'Q56'."""
    return float(PinNo(int(re.sub(r"\D", "", pin_name))))


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

    # Analog Inputs AI1 to AI8 along left margin (same physical slots)
    for i in range(1, 9):
        pin_name = f"AI{i}"
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

    # Q56: extra output between Q5 and Q6 (drawn only if an exercise uses it)
    pins["Q56"] = TerminalPin(
        name="Q56",
        direction="output",
        x=SVG_W,
        y=pin_slot("Q56") * UNITS_PER_CM,
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


def assign_connection_tracks(conns: List[Dict]) -> List[int]:
    """Assigns collision-free vertical track indices (0, 1, 2, ...) to a set of connections
    sharing a routing channel (e.g. left input margin or right output margin).
    Uses combinatorial optimization to guarantee that lines dropping or rising past other
    pins take outer tracks, preventing wires from cutting across horizontal take-off segments
    or overlapping vertical tracks.
    """
    n = len(conns)
    if n <= 1:
        return [0] * n

    def evaluate_cost(conns_subset, assignment):
        m = len(conns_subset)
        cost = sum(assignment)
        for i in range(m):
            for j in range(i + 1, m):
                ci, cj = conns_subset[i], conns_subset[j]
                ti, tj = assignment[i], assignment[j]

                # 1. Overlapping vertical segments on the exact same track
                if ci['needs_bend'] and cj['needs_bend'] and ti == tj:
                    y_min_i, y_max_i = min(ci['sy'], ci['dy']), max(ci['sy'], ci['dy'])
                    y_min_j, y_max_j = min(cj['sy'], cj['dy']), max(cj['sy'], cj['dy'])
                    if max(y_min_i, y_min_j) < min(y_max_i, y_max_j) - 1.0:
                        cost += 10000

                # 2. ci vertical segment cuts cj pin take-off
                if ci['needs_bend'] and abs(ci['pin_y'] - cj['pin_y']) > 1.0:
                    y_min_i, y_max_i = min(ci['sy'], ci['dy']), max(ci['sy'], ci['dy'])
                    if y_min_i - 1.0 <= cj['pin_y'] <= y_max_i + 1.0:
                        if ti <= tj:
                            cost += 5000 + (tj - ti + 1) * 1000

                # 2b. cj vertical segment cuts ci pin take-off
                if cj['needs_bend'] and abs(ci['pin_y'] - cj['pin_y']) > 1.0:
                    y_min_j, y_max_j = min(cj['sy'], cj['dy']), max(cj['sy'], cj['dy'])
                    if y_min_j - 1.0 <= ci['pin_y'] <= y_max_j + 1.0:
                        if tj <= ti:
                            cost += 5000 + (ti - tj + 1) * 1000

                # 3. Unnecessary arrival segment cuts (when signals do not cross)
                not_crossing = ((ci['sy'] - cj['sy']) * (ci['dy'] - cj['dy']) > 0)
                if not_crossing:
                    if cj['needs_bend']:
                        y_min_j, y_max_j = min(cj['sy'], cj['dy']), max(cj['sy'], cj['dy'])
                        if y_min_j - 1.0 <= ci['other_y'] <= y_max_j + 1.0:
                            if tj >= ti:
                                cost += 2000
                    if ci['needs_bend']:
                        y_min_i, y_max_i = min(ci['sy'], ci['dy']), max(ci['sy'], ci['dy'])
                        if y_min_i - 1.0 <= cj['other_y'] <= y_max_i + 1.0:
                            if ti >= tj:
                                cost += 2000

                # 4. Corner touch on crossing signals
                crossing = ((ci['sy'] - cj['sy']) * (ci['dy'] - cj['dy']) < 0)
                if crossing and ci['needs_bend'] and cj['needs_bend']:
                    if ti == tj:
                        cost += 3000

                # 5. Near-horizontal parallel line collision between pin take-off and arrival segment
                if abs(ci['other_y'] - cj['pin_y']) < 8.0:
                    if ti <= tj:
                        cost += 5000 + (tj - ti + 1) * 1000
                if abs(cj['other_y'] - ci['pin_y']) < 8.0:
                    if tj <= ti:
                        cost += 5000 + (ti - tj + 1) * 1000
        return cost

    num_tracks = min(n, 5)
    domains = []
    for c in conns:
        if not c['needs_bend']:
            domains.append([0])
        else:
            domains.append(list(range(num_tracks)))

    total_states = 1
    for d in domains:
        total_states *= len(d)

    # Exhaustive search for small problem sizes (<= 4096 combinations)
    if total_states <= 4096:
        best_assignment = None
        best_cost = float('inf')
        for assignment in itertools.product(*domains):
            cost = evaluate_cost(conns, assignment)
            if cost < best_cost:
                best_cost = cost
                best_assignment = list(assignment)
        return best_assignment if best_assignment is not None else [0] * n

    # Greedy constructive pass for larger sets
    assignment = [0] * n
    for i in range(n):
        if not conns[i]['needs_bend']:
            assignment[i] = 0
            continue
        best_t = 0
        best_c = float('inf')
        for t in range(num_tracks):
            assignment[i] = t
            c = evaluate_cost(conns[:i+1], assignment[:i+1])
            if c < best_c:
                best_c = c
                best_t = t
        assignment[i] = best_t

    # Hill-climbing refinement passes
    improved = True
    passes = 0
    while improved and passes < 5:
        improved = False
        passes += 1
        for i in range(n):
            if not conns[i]['needs_bend']:
                continue
            cur_best = assignment[i]
            cur_cost = evaluate_cost(conns, assignment)
            for t in range(num_tracks):
                if t == cur_best:
                    continue
                assignment[i] = t
                new_cost = evaluate_cost(conns, assignment)
                if new_cost < cur_cost:
                    cur_cost = new_cost
                    cur_best = t
                    improved = True
            assignment[i] = cur_best

    return assignment


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

    # 3. Classify instances into IO pins, pass-throughs, and Logic blocks
    io_map = {}  # instance_name -> pin_name (e.g. 'DigitalInput_I1' -> 'I1')
    logic_instances = []
    passthroughs = []

    for inst in model.instances:
        pt = identify_passthrough(inst)
        if pt:
            passthroughs.append((inst, pt[0], pt[1], pt[2]))
            continue
        pin = identify_io_pin(inst)
        if pin:
            io_map[inst.name] = pin
        else:
            logic_instances.append(inst)

    pins = get_pin_positions()

    # Scale block geometry (placement uses the scaled sizes, rendering draws the original and scales the group)
    block_orig = {}
    for inst in logic_instances:
        block_orig[inst.name] = (inst.block_width, inst.block_height, inst.name_section_bottom,
                                 getattr(inst, "adapter_section_top", None))
        inst.block_width *= BLOCK_SCALE
        inst.block_height *= BLOCK_SCALE
        inst.name_section_bottom *= BLOCK_SCALE
        if getattr(inst, "adapter_section_top", None) is not None:
            inst.adapter_section_top *= BLOCK_SCALE
    port_row = renderer.PORT_ROW_HEIGHT * BLOCK_SCALE

    # 4. Map connections and find active pins
    card_connections = []
    active_pins = set()

    # Add synthesized connections for pass-through instances (e.g. logiBUS_IXA_TO_logiBUS_QXA)
    for inst, in_pin, out_pin, conn_type in passthroughs:
        active_pins.add(in_pin)
        active_pins.add(out_pin)
        synth_conn = Connection(
            source=f"{in_pin}.OUT",
            destination=f"{out_pin}.IN",
            conn_type=conn_type
        )
        card_connections.append({
            "conn": synth_conn,
            "source_pin": in_pin,
            "source_inst": None,
            "source_port": "",
            "dest_pin": out_pin,
            "dest_inst": None,
            "dest_port": "",
            "color": renderer.ADAPTER_PORT_COLOR if conn_type == "adapter" else renderer.BOOL_PORT_COLOR,
            "double_line": (conn_type == "adapter")
        })

    inst_by_name = {inst.name: inst for inst in model.instances}

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

        event_name = None
        event_label = None
        src_fb = inst_by_name.get(src_inst)
        if src_fb:
            event_name = src_fb.parameters.get("InputEvent")
            if event_name:
                event_name = event_name.split("::")[-1].strip().strip('"\'')
            if not event_name and "BUTTON_" in src_fb.name:
                event_name = src_fb.name
            if event_name:
                event_label = EVENT_LABELS.get(event_name)

        card_connections.append({
            "conn": conn,
            "source_pin": source_pin,
            "source_inst": None if source_pin else src_inst,
            "source_port": src_parts[1] if len(src_parts) > 1 else "",
            "dest_pin": dest_pin,
            "dest_inst": None if dest_pin else dst_inst,
            "dest_port": dst_parts[1] if len(dst_parts) > 1 else "",
            "event_name": event_name,
            "event_label": event_label,
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
        min_4d_x = min(inst.x for inst in logic_instances)
        max_4d_x = max(inst.x for inst in logic_instances)
        min_4d_y = min(inst.y for inst in logic_instances)
        max_4d_y = max(inst.y for inst in logic_instances)

        raw_span_x = max_4d_x - min_4d_x
        span_4d_y = max(0.0, max_4d_y - min_4d_y)

        x_safe_min = 48.0
        x_safe_max = 285.0
        y_safe_min = 35.0
        y_safe_max = 395.0

        # Horizontal placement: compute render_x first to know exact horizontal block extents
        if raw_span_x < 50.0:
            for inst in logic_instances:
                inst.render_x = (SVG_W - inst.block_width) / 2.0
        else:
            for inst in logic_instances:
                norm_x = (inst.x - min_4d_x) / raw_span_x
                inst_avail_w = max(0.0, (x_safe_max - x_safe_min) - inst.block_width)
                inst.render_x = x_safe_min + norm_x * inst_avail_w

        # Blocks in the leftmost column that are fed directly by input pins get 1 cm extra room, so the
        # event/data wires from the pins have space (skipped if the shift would make blocks overlap horizontally)
        fed_by_pin = {c["dest_inst"] for c in card_connections if c.get("source_pin") and c.get("dest_inst")}
        for inst in logic_instances:
            if inst.name not in fed_by_pin or inst.x != min_4d_x:
                continue
            shift = UNITS_PER_CM
            new_x = inst.render_x + shift
            if new_x + inst.block_width > x_safe_max:
                continue
            def x_overlap(a_x, a_w, b):
                return a_x < b.render_x + b.block_width and b.render_x < a_x + a_w
            if any(o is not inst and not x_overlap(inst.render_x, inst.block_width, o)
                   and x_overlap(new_x, inst.block_width, o) for o in logic_instances):
                continue
            inst.render_x = new_x

        # Snap blocks that are in different columns but placed on roughly the same row in 4diac (dy <= 60.0)
        # to the exact same row to prevent artificial vertical staggering, but only if they do not overlap horizontally
        sorted_logic = sorted(logic_instances, key=lambda inst: inst.y)
        for i in range(len(sorted_logic)):
            for j in range(i + 1, len(sorted_logic)):
                inst_a = sorted_logic[i]
                inst_b = sorted_logic[j]
                horiz_overlap = (inst_a.render_x < inst_b.render_x + inst_b.block_width and
                                 inst_b.render_x < inst_a.render_x + inst_a.block_width)
                if abs(inst_a.y - inst_b.y) <= 60.0 and abs(inst_a.x - inst_b.x) > 300.0 and not horiz_overlap:
                    inst_b.y = inst_a.y

        max_block_h = max(inst.block_height for inst in logic_instances)
        avail_h = max(0.0, (y_safe_max - y_safe_min) - max_block_h)

        # Calculate minimum vertical scale to prevent any blocks in the same column or horizontally overlapping from colliding
        min_scale_needed = 0.05
        for i in range(len(logic_instances)):
            for j in range(len(logic_instances)):
                if i == j:
                    continue
                inst_a = logic_instances[i]
                inst_b = logic_instances[j]
                dy_4d = inst_b.y - inst_a.y
                horiz_overlap = (inst_a.render_x < inst_b.render_x + inst_b.block_width and
                                 inst_b.render_x < inst_a.render_x + inst_a.block_width)
                in_same_column = horiz_overlap or (abs(inst_a.x - inst_b.x) <= 400.0)
                if dy_4d > 10.0 and in_same_column:
                    req_scale = (inst_a.block_height + BLOCK_LABEL_GAP) / dy_4d
                    if req_scale > min_scale_needed:
                        min_scale_needed = req_scale

        max_scale_y = avail_h / span_4d_y if span_4d_y > 0 else 0.05
        # Ensure scale is large enough to prevent collisions while fitting on card
        scale_y = min(max_scale_y, max(0.05, min_scale_needed))
        group_h = span_4d_y * scale_y + max_block_h

        connected_ys = [pins[p].y for p in active_pins if p in pins]
        if connected_ys:
            target_mid_y = sum(connected_ys) / len(connected_ys)
        else:
            target_mid_y = (y_safe_min + y_safe_max) / 2.0

        group_top_y = target_mid_y - group_h / 2.0
        group_top_y = max(y_safe_min, min(group_top_y, y_safe_max - group_h))

        for inst in logic_instances:
            inst.render_y = group_top_y + (inst.y - min_4d_y) * scale_y

        # Blocks that still overlap (the 4diac y-spacing was compressed too much to fit the card) are stacked
        # on top of each other in 4diac order within the remaining free space
        def overlaps(a, b, gap):
            return (a.render_x < b.render_x + b.block_width and b.render_x < a.render_x + a.block_width and
                    a.render_y < b.render_y + b.block_height + gap and b.render_y < a.render_y + a.block_height + gap)

        if any(overlaps(a, b, 0.0) for i, a in enumerate(logic_instances) for b in logic_instances[i + 1:]):
            # Stacking order follows the data flow (sources above sinks), not the 4diac y-position
            names = {i.name for i in logic_instances}
            links = {(c["source_inst"], c["dest_inst"]) for c in card_connections
                     if c.get("source_inst") in names and c.get("dest_inst") in names
                     and c["source_inst"] != c["dest_inst"]}
            depth = {n: 0 for n in names}
            for _ in range(len(names)):
                for s, d in links:
                    if depth[d] < depth[s] + 1 and depth[s] + 1 < len(names):
                        depth[d] = depth[s] + 1
            def flow_key(i):
                return (depth[i.name], i.render_y, i.y)
            for gap in (10.0, 6.0, 3.0):
                for inst in logic_instances:
                    inst.render_y = group_top_y + (inst.y - min_4d_y) * scale_y
                order = sorted(logic_instances, key=flow_key)
                for _ in range(len(order)):
                    moved = False
                    for bi, b in enumerate(order):
                        for a in order[:bi]:
                            if overlaps(a, b, gap):
                                b.render_y = a.render_y + a.block_height + gap
                                moved = True
                    if not moved:
                        break
                if max(i.render_y + i.block_height for i in logic_instances) <= y_safe_max:
                    break
            # Close gaps left by the compressed spacing (blocks move up, in order), then spread the
            # remaining free space evenly between the stacked blocks
            order = sorted(logic_instances, key=flow_key)
            for bi, b in enumerate(order):
                above = [a.render_y + a.block_height + gap for a in order[:bi]
                         if a.render_x < b.render_x + b.block_width and b.render_x < a.render_x + a.block_width]
                b.render_y = max([y_safe_min] + above)
            stacked = [bi for bi, b in enumerate(order)
                       if any(a.render_x < b.render_x + b.block_width and b.render_x < a.render_x + a.block_width
                              for a in order[:bi])]
            free = y_safe_max - max(i.render_y + i.block_height for i in logic_instances)
            if stacked and free > 0:
                extra = min(20.0, free / len(stacked))
                for bi, b in enumerate(order):
                    b.render_y += extra * sum(1 for s in stacked if s <= bi)

    # Final safety net: a column can still be too tall to fit the card after stacking at the
    # minimum gap (too many blocks, or a single block that is inherently very tall/wide, e.g.
    # Uebung_028c2_AR or Uebung_009a_AX). Shrink just the blocks of that column further, in place
    # around their own center, until the whole column fits within the card's safe area.
    for inst in logic_instances:
        inst.extra_scale = 1.0

    def _x_overlap(a, b):
        return a.render_x < b.render_x + b.block_width and b.render_x < a.render_x + a.block_width

    remaining = list(logic_instances)
    columns = []
    while remaining:
        column = [remaining.pop()]
        changed = True
        while changed:
            changed = False
            for inst in remaining[:]:
                if any(_x_overlap(inst, c) for c in column):
                    column.append(inst)
                    remaining.remove(inst)
                    changed = True
        columns.append(column)

    # Blocks are stacked with the same BLOCK_LABEL_GAP clearance used elsewhere (rendered-space,
    # calibrated for extra_scale=1.0); it shrinks together with the blocks themselves so the
    # instance name above each block never collides with the block above it.
    for column in columns:
        column.sort(key=lambda i: i.render_y)
        sum_h = sum(i.block_height for i in column)
        if sum_h <= 0:
            continue
        n = len(column)
        needed = sum_h + (n - 1) * BLOCK_LABEL_GAP
        top_y_current = min(i.render_y for i in column)
        top_y = 35.0 if needed > (395.0 - top_y_current) else top_y_current
        avail = 395.0 - top_y
        if needed <= avail:
            continue
        shrink = max(0.01, avail / needed)
        if shrink >= 1.0:
            continue
        y = top_y
        for inst in column:
            old_w = inst.block_width
            inst.block_width *= shrink
            inst.block_height *= shrink
            inst.name_section_bottom *= shrink
            if getattr(inst, "adapter_section_top", None) is not None:
                inst.adapter_section_top *= shrink
            inst.extra_scale *= shrink
            inst.render_x += (old_w - inst.block_width) / 2.0
            inst.render_y = y
            y += inst.block_height + BLOCK_LABEL_GAP * shrink

    # Snap blocks fed by input pins to the 1 cm pin grid: shift each block so that the port of its topmost
    # nearly aligned pin->port connection (max. 20 units off) sits exactly at the pin height; the other
    # ports keep their fixed spacing and are bent normally by the router
    def in_port_dy(inst, port_name):
        extra = inst.extra_scale
        row = port_row * extra
        for k, port in enumerate(inst.event_inputs):
            if port.name == port_name:
                return 2 * BLOCK_SCALE * extra + row / 2 + k * row
        for k, port in enumerate(inst.data_inputs):
            if port.name == port_name:
                return inst.name_section_bottom + 2 * BLOCK_SCALE * extra + row / 2 + k * row
        return None

    inst_by_name_snap = {i.name: i for i in logic_instances}
    for inst in logic_instances:
        diffs = []
        for c in card_connections:
            if c.get("source_pin") in pins and c.get("dest_inst") == inst.name:
                dy_port = in_port_dy(inst, c.get("dest_port"))
                if dy_port is not None:
                    d = pins[c["source_pin"]].y - (inst.render_y + dy_port)
                    if abs(d) <= 20.0:
                        diffs.append((pins[c["source_pin"]].y, d))
        if not diffs:
            continue
        shift = min(diffs)[1]
        new_y = inst.render_y + shift
        if new_y < 30.0 or new_y + inst.block_height > 395.0:
            continue
        old_y = inst.render_y
        inst.render_y = new_y
        if any(o is not inst and o.render_x < inst.render_x + inst.block_width and inst.render_x < o.render_x + o.block_width
               and o.render_y < inst.render_y + inst.block_height + 4.0 and inst.render_y < o.render_y + o.block_height + 4.0
               for o in logic_instances):
            inst.render_y = old_y

    # Block-to-block connections whose ports are (almost) vertically above each other would be routed as a
    # straight vertical line; give them room for a Z (destination block right, then source block left)
    Z_MIN_GAP = 24.0
    X_MAX_RIGHT = 300.0
    X_MIN_LEFT = 60.0
    inst_names_z = {i.name: i for i in logic_instances}

    def x_clash(inst):
        return any(o is not inst and o.render_x < inst.render_x + inst.block_width and inst.render_x < o.render_x + o.block_width
                   and o.render_y < inst.render_y + inst.block_height + 4.0 and inst.render_y < o.render_y + o.block_height + 4.0
                   for o in logic_instances)

    for c in card_connections:
        a = inst_names_z.get(c.get("source_inst"))
        b = inst_names_z.get(c.get("dest_inst"))
        if a is None or b is None or a is b:
            continue
        gap = b.render_x - (a.render_x + a.block_width)
        if not (0.0 <= gap < Z_MIN_GAP) or abs(a.render_y - b.render_y) < 2.0:
            continue
        need = Z_MIN_GAP - gap
        old_bx, old_ax = b.render_x, a.render_x
        b.render_x += max(0.0, min(need, X_MAX_RIGHT - (b.render_x + b.block_width)))
        need -= b.render_x - old_bx
        if need > 0.0:
            a.render_x -= max(0.0, min(need, a.render_x - X_MIN_LEFT))
        if x_clash(a) or x_clash(b):
            a.render_x, b.render_x = old_ax, old_bx

    # Recompute port positions on the placed logic instances
    instance_map = {}
    for inst in logic_instances:
        instance_map[inst.name] = inst
        inst.port_positions = {}
        extra = inst.extra_scale
        inst_port_row = port_row * extra
        top_offset = 2 * BLOCK_SCALE * extra
        # Event inputs
        y = inst.render_y + top_offset + inst_port_row / 2
        for port in inst.event_inputs:
            inst.port_positions[port.name] = (inst.render_x, y)
            y += inst_port_row
        # Event outputs
        y = inst.render_y + top_offset + inst_port_row / 2
        for port in inst.event_outputs:
            inst.port_positions[port.name] = (inst.render_x + inst.block_width, y)
            y += inst_port_row
        # Data inputs
        y = inst.render_y + inst.name_section_bottom + top_offset + inst_port_row / 2
        for port in inst.data_inputs:
            inst.port_positions[port.name] = (inst.render_x, y)
            y += inst_port_row
        # Data outputs
        y = inst.render_y + inst.name_section_bottom + top_offset + inst_port_row / 2
        for port in inst.data_outputs:
            inst.port_positions[port.name] = (inst.render_x + inst.block_width, y)
            y += inst_port_row
        # Sockets (adapter inputs)
        y = inst.render_y + inst.adapter_section_top + top_offset + inst_port_row / 2
        for port in inst.sockets:
            inst.port_positions[port.name] = (inst.render_x, y)
            y += inst_port_row
        # Plugs (adapter outputs)
        y = inst.render_y + inst.adapter_section_top + top_offset + inst_port_row / 2
        for port in inst.plugs:
            inst.port_positions[port.name] = (inst.render_x + inst.block_width, y)
            y += inst_port_row

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

    # Pre-calculate points and assign collision-free tracks for input & output pins
    for cinfo in card_connections:
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

        cinfo["src_pt"] = src_pt
        cinfo["dst_pt"] = dst_pt

    left_conns = []
    for cinfo in card_connections:
        if cinfo["source_pin"] and not cinfo.get("dest_pin") and cinfo.get("src_pt") and cinfo.get("dst_pt"):
            sx, sy = cinfo["src_pt"]
            dx, dy = cinfo["dst_pt"]
            if sx <= dx:
                left_conns.append({
                    "cinfo": cinfo,
                    "sy": sy,
                    "dy": dy,
                    "pin_y": sy,
                    "other_y": dy,
                    "needs_bend": abs(sy - dy) >= 2.0,
                    "sx": sx,
                    "dx": dx,
                })

    right_conns = []
    for cinfo in card_connections:
        if cinfo["dest_pin"] and not cinfo.get("source_pin") and cinfo.get("src_pt") and cinfo.get("dst_pt"):
            sx, sy = cinfo["src_pt"]
            dx, dy = cinfo["dst_pt"]
            if sx <= dx:
                right_conns.append({
                    "cinfo": cinfo,
                    "sy": sy,
                    "dy": dy,
                    "pin_y": dy,
                    "other_y": sy,
                    "needs_bend": abs(sy - dy) >= 2.0,
                    "sx": sx,
                    "dx": dx,
                })

    # Event lines run slightly offset from data lines (wires leaving one pin towards an event and a
    # data port would otherwise be drawn exactly on top of each other)
    EVENT_LINE_OFFSET = 3.0
    inst_by_name_all = {inst.name: inst for inst in model.instances}

    def is_event_port(inst_name, port_name, outputs):
        inst = inst_by_name_all.get(inst_name)
        if inst is None:
            return False
        ports = inst.event_outputs if outputs else inst.event_inputs
        return any(p.name == port_name for p in ports)

    def share_tracks(conns, tracks, key):
        """Connections of the same signal (same destination/source port) share one vertical track."""
        best = {}
        for item, tr in zip(conns, tracks):
            k = key(item["cinfo"])
            if k[0] is not None and item["needs_bend"]:
                best[k] = min(best.get(k, tr), tr)
        return [best.get(key(item["cinfo"]), tr) if item["needs_bend"] else tr
                for item, tr in zip(conns, tracks)]

    left_tracks = share_tracks(left_conns, assign_connection_tracks(left_conns),
                               lambda c: (c.get("dest_inst"), c.get("dest_port")))
    right_tracks = share_tracks(right_conns, assign_connection_tracks(right_conns),
                                lambda c: (c.get("source_inst"), c.get("source_port")))

    def place_tracks(conns, tracks, outputs):
        """Data lines take their own tracks; all event lines of a channel (one signal per port) run
        on a common x in the middle between the outermost data lines (default: slightly offset)."""
        left = conns is left_conns
        def base_x(item, tr):
            if left:
                return min(item["dx"] - 12.0, item["sx"] + 18.0 + tr * 6.0)
            return max(item["sx"] + 12.0, item["dx"] - 18.0 - tr * 6.0)
        is_ev = []
        for item in conns:
            ci = item["cinfo"]
            name, port = (ci.get("source_inst"), ci.get("source_port")) if outputs else (ci.get("dest_inst"), ci.get("dest_port"))
            is_ev.append(is_event_port(name, port, outputs))
        data_x = [base_x(it, tr) for it, tr, ev in zip(conns, tracks, is_ev) if not ev and it["needs_bend"]]
        mid = (min(data_x) + max(data_x)) / 2.0 if len(set(data_x)) > 1 else None
        for item, tr, ev in zip(conns, tracks, is_ev):
            x = base_x(item, tr)
            if ev:
                x = mid if (mid is not None and item["needs_bend"]) else x + (EVENT_LINE_OFFSET if left else -EVENT_LINE_OFFSET)
                x = min(item["dx"] - 12.0, x) if left else max(item["sx"] + 12.0, x)
            item["cinfo"]["assigned_mid_x"] = x

    place_tracks(left_conns, left_tracks, False)
    place_tracks(right_conns, right_tracks, True)

    # Internal block-to-block connections (sx <= dx) that share a vertical routing channel
    internal_conns = []
    for cinfo in card_connections:
        if not cinfo.get("source_pin") and not cinfo.get("dest_pin") and cinfo.get("src_pt") and cinfo.get("dst_pt"):
            sx, sy = cinfo["src_pt"]
            dx, dy = cinfo["dst_pt"]
            if sx <= dx and abs(sy - dy) >= 2.0:
                internal_conns.append({
                    "cinfo": cinfo,
                    "sx": sx,
                    "dx": dx,
                    "sy": sy,
                    "dy": dy,
                    "y_min": min(sy, dy),
                    "y_max": max(sy, dy),
                    "dest": (cinfo.get("dest_inst"), cinfo.get("dest_port")),
                    "src": (cinfo.get("source_inst"), cinfo.get("source_port")),
                })

    # Group internal_conns into horizontal channels
    channels = []
    for iconn in internal_conns:
        matched = False
        for chan in channels:
            chan_sx = max(c["sx"] for c in chan)
            chan_dx = min(c["dx"] for c in chan)
            if max(chan_sx, iconn["sx"]) < min(chan_dx, iconn["dx"]) - 10.0:
                chan.append(iconn)
                matched = True
                break
        if not matched:
            channels.append([iconn])

    for chan in channels:
        if len(chan) <= 1:
            continue
        needs_tracks = False
        for i in range(len(chan)):
            for j in range(i + 1, len(chan)):
                if max(chan[i]["y_min"], chan[j]["y_min"]) < min(chan[i]["y_max"], chan[j]["y_max"]) - 1.0:
                    needs_tracks = True
                    break
            if needs_tracks:
                break
        if not needs_tracks:
            continue

        chan_sx = max(c["sx"] for c in chan)
        chan_dx = min(c["dx"] for c in chan)
        mid_base = (chan_sx + chan_dx) / 2.0

        def eval_chan_cost(c_list, assignment):
            cost = 0
            m = len(c_list)
            for i in range(m):
                for j in range(i + 1, m):
                    ci, cj = c_list[i], c_list[j]
                    ti, tj = assignment[i], assignment[j]
                    if ti == tj:
                        if max(ci["y_min"], cj["y_min"]) < min(ci["y_max"], cj["y_max"]) - 1.0:
                            cost += 10000
                        elif ci["dest"] == cj["dest"]:
                            cost -= 500
                        elif ci["src"] == cj["src"]:
                            cost -= 500
                    elif ti < tj:
                        if ci["y_min"] - 0.5 <= cj["sy"] <= ci["y_max"] + 0.5:
                            cost += 2000
                        if cj["y_min"] - 0.5 <= ci["dy"] <= cj["y_max"] + 0.5:
                            cost += 2000
                    else:
                        if cj["y_min"] - 0.5 <= ci["sy"] <= cj["y_max"] + 0.5:
                            cost += 2000
                        if ci["y_min"] - 0.5 <= cj["dy"] <= ci["y_max"] + 0.5:
                            cost += 2000
            return cost

        best_assignment = None
        for num_tracks in range(2, min(len(chan) + 1, 5)):
            domains = [list(range(num_tracks)) for _ in chan]
            combos = list(itertools.product(*domains))
            best_cost = float("inf")
            cur_best = None
            for a in combos:
                c = eval_chan_cost(chan, a)
                if c < best_cost:
                    best_cost = c
                    cur_best = a
            if cur_best and best_cost < 10000:
                best_assignment = cur_best
                break
            best_assignment = cur_best

        if best_assignment:
            unique_tracks = sorted(list(set(best_assignment)))
            k = len(unique_tracks)
            track_rank = {t: idx for idx, t in enumerate(unique_tracks)}
            step = min(8.0, (chan_dx - chan_sx - 24.0) / max(1, k - 1)) if k > 1 else 0.0
            for item, t in zip(chan, best_assignment):
                rank = track_rank[t]
                track_x = mid_base - (k - 1) * step / 2.0 + rank * step
                item["cinfo"]["assigned_mid_x"] = max(chan_sx + 10.0, min(chan_dx - 10.0, track_x))

    # Connections group (rendered behind blocks)
    svg.append('  <g id="connections">')
    for cinfo in card_connections:
        conn = cinfo["conn"]
        src_pt = cinfo.get("src_pt")
        dst_pt = cinfo.get("dst_pt")

        if src_pt and dst_pt:
            sx, sy = src_pt
            dx, dy = dst_pt

            if abs(sy - dy) < 2.0 and sx <= dx:
                waypoints = [src_pt, dst_pt]
            elif sx > dx:
                # Feedback or vertical cascade from right-side output to left-side input
                # Route out of the right port, down/up through the inter-block gap, and into the left port
                src_inst_obj = instance_map.get(cinfo.get("source_inst"))
                dst_inst_obj = instance_map.get(cinfo.get("dest_inst"))
                if src_inst_obj and dst_inst_obj:
                    if src_inst_obj == dst_inst_obj:
                        gap_y = src_inst_obj.render_y + src_inst_obj.block_height + 12.0
                    elif dy > sy:
                        gap_y = (src_inst_obj.render_y + src_inst_obj.block_height + dst_inst_obj.render_y) / 2.0
                    else:
                        gap_y = (dst_inst_obj.render_y + dst_inst_obj.block_height + src_inst_obj.render_y) / 2.0
                else:
                    gap_y = (sy + dy) / 2.0

                out_x = sx + 14.0
                in_x = dx - 14.0
                # Event wires of a block-to-block cascade run slightly offset (x and y) from the data wires so both
                # stay visible without crossing. Event ports sit above data ports: going down the event wire is the
                # outer one at the first bend and the inner one at the last; going up it is the other way round
                if is_event_port(cinfo.get("source_inst"), cinfo.get("source_port"), True):
                    sign = 1.0 if dy > sy else -1.0
                    out_x += 4.0 * sign
                    in_x += 4.0 * sign
                    gap_y += 4.0
                waypoints = [
                    (sx, sy),
                    (out_x, sy),
                    (out_x, gap_y),
                    (in_x, gap_y),
                    (in_x, dy),
                    (dx, dy)
                ]
            else:
                if "assigned_mid_x" in cinfo:
                    mid_x = cinfo["assigned_mid_x"]
                else:
                    mid_x = (sx + dx) / 2.0

                waypoints = [
                    (sx, sy),
                    (mid_x, sy),
                    (mid_x, dy),
                    (dx, dy)
                ]

            if conn and conn.conn_type == "adapter":
                color = renderer.ADAPTER_PORT_COLOR
                is_double = True
            elif conn and hasattr(renderer, "_get_connection_color"):
                try:
                    color = renderer._get_connection_color(conn, model, instance_map)
                    is_double = renderer._is_double_line_connection(conn, model, instance_map)
                except Exception:
                    color = cinfo.get("color", renderer.BOOL_PORT_COLOR)
                    is_double = cinfo.get("double_line", False)
            else:
                color = cinfo.get("color", renderer.BOOL_PORT_COLOR)
                is_double = cinfo.get("double_line", False)

            cinfo["waypoints"] = waypoints
            cinfo["color"] = color
            svg.append(renderer._render_connection(waypoints, color, double_line=is_double))

    # Connection event labels (pills) for multi-event or special event pins
    pin_events = defaultdict(set)
    for cinfo in card_connections:
        spin = cinfo.get("source_pin")
        ev_name = cinfo.get("event_name")
        if spin and ev_name:
            pin_events[spin].add(ev_name)

    labeled_conns = []
    for cinfo in card_connections:
        ev_label = cinfo.get("event_label")
        ev_name = cinfo.get("event_name")
        spin = cinfo.get("source_pin")
        if not ev_label or not cinfo.get("waypoints"):
            continue
        is_multi_event = spin and len(pin_events.get(spin, set())) > 1
        is_special_event = ev_name and ev_name != "BUTTON_SINGLE_CLICK"
        if is_multi_event or is_special_event:
            labeled_conns.append(cinfo)

    pin_groups = defaultdict(list)
    for cinfo in labeled_conns:
        spin = cinfo.get("source_pin")
        if spin:
            pin_groups[spin].append(cinfo)
        else:
            pin_groups[id(cinfo)].append(cinfo)

    for group_key, grp in pin_groups.items():
        horiz_conns = []
        for cinfo in grp:
            wps = cinfo["waypoints"]
            if len(wps) >= 2:
                p_start = wps[-2]
                p_end = wps[-1]
                if abs(p_start[1] - p_end[1]) < 1.0 and p_end[0] > p_start[0] + 20.0:
                    horiz_conns.append((cinfo, p_start, p_end))

        if not horiz_conns:
            continue

        max_start_x = max(p_s[0] for _, p_s, _ in horiz_conns)
        min_end_x = min(p_e[0] for _, _, p_e in horiz_conns)
        max_text_len = max(len(cinfo["event_label"]) for cinfo, _, _ in horiz_conns)
        grp_pill_w = max(36.0, max_text_len * 4.2 + 8.0)

        can_align = (min_end_x - max_start_x) >= (grp_pill_w + 10.0)
        shared_x = (max_start_x + min_end_x) / 2.0 if can_align else None

        for cinfo, p_start, p_end in horiz_conns:
            ev_label = cinfo["event_label"]
            lbl_x = shared_x if shared_x is not None else (p_start[0] + p_end[0]) / 2.0
            lbl_y = p_end[1]
            pill_w = max(36.0, len(ev_label) * 4.2 + 8.0)
            pill_h = 7.5

            svg.append(f'    <rect x="{lbl_x - pill_w/2.0:.1f}" y="{lbl_y - 1.5 - pill_h:.1f}" width="{pill_w:.1f}" height="{pill_h:.1f}" rx="2" fill="#FFFFFF" fill-opacity="0.95" stroke="#BDC3C7" stroke-width="0.6"/>')
            svg.append(f'    <text x="{lbl_x:.1f}" y="{lbl_y - 3.3:.1f}" font-family="\'TGL 0-17_std\', \'TGL 0-17\', Helvetica, Arial, sans-serif" font-size="6.8" font-weight="bold" fill="#2C3E50" text-anchor="middle">{_xml_escape(ev_label)}</text>')

    svg.append('  </g>')

    # Render logic FB instances
    svg.append('  <g id="instances">')
    for inst in logic_instances:
        bw, bh, nsb, ast = block_orig[inst.name]
        scaled = (inst.block_width, inst.block_height, inst.name_section_bottom, getattr(inst, "adapter_section_top", None))
        inst.block_width, inst.block_height, inst.name_section_bottom = bw, bh, nsb
        if ast is not None:
            inst.adapter_section_top = ast
        total_scale = BLOCK_SCALE * inst.extra_scale
        svg.append(f'  <g transform="translate({inst.render_x:.2f},{inst.render_y:.2f}) scale({total_scale}) '
                   f'translate({-inst.render_x:.2f},{-inst.render_y:.2f})">')
        svg.append(renderer._render_instance(inst))
        svg.append('  </g>')
        inst.block_width, inst.block_height, inst.name_section_bottom = scaled[:3]
        if ast is not None:
            inst.adapter_section_top = scaled[3]
    svg.append('  </g>')

    # Left margin pins: I1 to I8 and AI1 to AI8 (only if used!)
    for i in range(1, 9):
        for pin_name in (f"I{i}", f"AI{i}"):
            if pin_name not in active_pins:
                continue
            py = i * UNITS_PER_CM
            # Semicircle / half-pill directly at x = 0 (radius = 13.5, height = 27, depth = 15)
            svg.append(f'  <path d="M 0,{py-13.5:.1f} L 2,{py-13.5:.1f} A 13.5,13.5 0 0,1 2,{py+13.5:.1f} L 0,{py+13.5:.1f} Z" fill="#FFFFFF" stroke="#2C3E50" stroke-width="1.2"/>')
            # Center marker (+)
            svg.append(f'  <line x1="12" y1="{py}" x2="15" y2="{py}" stroke="#BDC3C7" stroke-width="0.6"/>')
            # Label in TGL font
            font_size = "8" if len(pin_name) > 2 else "9.5"
            svg.append(f'  <text x="7" y="{py+3.5:.1f}" font-family="\'TGL 0-17_std\', \'TGL 0-17\', Helvetica, Arial, sans-serif" font-size="{font_size}" font-weight="bold" fill="#2C3E50" text-anchor="middle">{pin_name}</text>')

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

    # Q56: extra output between Q5 and Q6 (only if used!); slimmer badge as it sits 0.5 cm from its neighbours
    if "Q56" in active_pins:
        py = pins["Q56"].y
        svg.append(f'  <path d="M {SVG_W},{py-10.5:.1f} L {SVG_W-2},{py-10.5:.1f} A 10.5,10.5 0 0,0 {SVG_W-2},{py+10.5:.1f} L {SVG_W},{py+10.5:.1f} Z" fill="#FFFFFF" stroke="#2C3E50" stroke-width="1.2"/>')
        svg.append(f'  <line x1="{SVG_W-15}" y1="{py}" x2="{SVG_W-12}" y2="{py}" stroke="#BDC3C7" stroke-width="0.6"/>')
        svg.append(f'  <text x="{SVG_W-7}" y="{py+3:.1f}" font-family="\'TGL 0-17_std\', \'TGL 0-17\', Helvetica, Arial, sans-serif" font-size="7.5" font-weight="bold" fill="#2C3E50" text-anchor="middle">Q56</text>')

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
    import io
    bio = io.BytesIO(svg_content.encode("utf-8"))
    drawing = svglib.svg2rlg(bio)
    if drawing:
        scale_x = w / drawing.width
        scale_y = h / drawing.height
        drawing.width = w
        drawing.height = h
        drawing.scale(scale_x, scale_y)
        renderPDF.draw(drawing, c, x, y)


def generate_single_card_pdf(subapp_file: str, output_pdf: str = "logiBUS_single_card.pdf"):
    """Generates a single-card PDF page centered on A4 with crop marks."""
    out_dir = os.path.dirname(output_pdf)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    svg_content = generate_card_svg(subapp_file)
    c = canvas.Canvas(output_pdf, pagesize=A4, invariant=1)
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
        comment_lines = wrap_text(comment, max_chars=80)
        curr_y = 3.0 * cm
        for cline in comment_lines[:4]:
            c.drawCentredString(page_w / 2.0, curr_y, cline)
            curr_y -= 0.4 * cm

    c.showPage()
    c.save()
    print(f"Generated single card PDF: {output_pdf}", flush=True)


def generate_multi_cards_pdf(subapp_files: List[str], output_pdf: str = "logiBUS_multi_cards.pdf"):
    """Generates a multi-card PDF with a 2x3 grid (6 cards per A4 page) for easy printing and cutting."""
    out_dir = os.path.dirname(output_pdf)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    c = canvas.Canvas(output_pdf, pagesize=A4, invariant=1)
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

    total_files = len(subapp_files)
    num_pages = (total_files + cards_per_page - 1) // cards_per_page

    print(f"\nStarte Generierung: {total_files} Karten auf {num_pages} DIN-A4-Seiten...", flush=True)

    for page_idx in range(num_pages):
        draw_crop_marks(c, start_x, start_y, grid_w, grid_h, length=8 * mm, offset=3 * mm)

        for slot in range(cards_per_page):
            idx = page_idx * cards_per_page + slot
            if idx >= total_files:
                break

            sub_file = subapp_files[idx]
            sub_name = os.path.splitext(os.path.basename(sub_file))[0]
            print(f"  [{idx + 1:3d}/{total_files}] (Seite {page_idx + 1:2d}/{num_pages}) {sub_name}...", flush=True)

            col = slot % cols
            row = slot // cols
            grid_row = (rows - 1) - row

            x = start_x + col * card_w
            y = start_y + grid_row * card_h

            try:
                svg_content = generate_card_svg(sub_file)
                render_card_on_pdf(c, svg_content, x, y, card_w, card_h)
            except Exception as e:
                print(f"    [WARNUNG] Fehler bei {sub_name}: {e}", flush=True)

            draw_crop_marks(c, x, y, card_w, card_h, length=4 * mm, offset=1.5 * mm)

        c.showPage()

    c.save()
    print(f"Generated multi card PDF: {output_pdf}\n", flush=True)


def draw_offset_crop_marks(c: canvas.Canvas, x: float, y: float, w: float, h: float, length: float = 3.5 * mm, offset: float = 1.5 * mm):
    """Draws professional offset printing crop marks outside the trim box."""
    c.setStrokeColor(colors.HexColor('#000000'))
    c.setLineWidth(0.25)  # Hairline

    # Bottom-Left corner (x, y)
    c.line(x - offset - length, y, x - offset, y)
    c.line(x, y - offset - length, x, y - offset)

    # Bottom-Right corner (x + w, y)
    c.line(x + w + offset, y, x + w + offset + length, y)
    c.line(x + w, y - offset - length, x + w, y - offset)

    # Top-Left corner (x, y + h)
    c.line(x - offset - length, y + h, x - offset, y + h)
    c.line(x, y + h + offset, x, y + h + offset + length)

    # Top-Right corner (x + w, y + h)
    c.line(x + w + offset, y + h, x + w + offset + length, y + h)
    c.line(x + w, y + h + offset, x + w, y + h + offset + length)


def generate_printshop_pdf(subapp_file: str, output_pdf: str = "logiBUS_printshop.pdf", bleed_mm: float = 3.0, slug_mm: float = 6.0):
    """Generates an offset print-ready PDF for commercial print shops.

    - TrimBox: exactly 70.0 mm x 90.0 mm (defining the final cut size / Endformat).
    - BleedBox: 76.0 mm x 96.0 mm (standard 3mm bleed).
    - MediaBox: 82.0 mm x 102.0 mm (with 6mm slug margin).
    - Crop marks (Schnittmarken): positioned outside the paper trim area pointing to the 70x90mm boundary.
    """
    out_dir = os.path.dirname(output_pdf)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    card_w = 7.0 * cm
    card_h = 9.0 * cm
    bleed = bleed_mm * mm
    margin = slug_mm * mm

    page_w = card_w + 2 * margin
    page_h = card_h + 2 * margin

    c = canvas.Canvas(output_pdf, pagesize=(page_w, page_h), invariant=1)

    # Set PDF prepress boxes
    c.setTrimBox((margin, margin, margin + card_w, margin + card_h))
    c.setBleedBox((margin - bleed, margin - bleed, margin + card_w + bleed, margin + card_h + bleed))

    # Fill BleedBox area with background color so trimming tolerance has full bleed
    c.setFillColor(colors.white)
    c.rect(margin - bleed, margin - bleed, card_w + 2 * bleed, card_h + 2 * bleed, fill=1, stroke=0)

    # Render card inside the TrimBox
    svg_content = generate_card_svg(subapp_file)
    render_card_on_pdf(c, svg_content, margin, margin, card_w, card_h)

    # Draw offset crop marks in the margin outside the trim box
    draw_offset_crop_marks(c, margin, margin, card_w, card_h, length=3.5 * mm, offset=1.5 * mm)

    c.showPage()
    c.save()
    print(f"Generated print shop offset PDF: {output_pdf}", flush=True)


def generate_exact_size_pdf(subapp_file: str, output_pdf: str = "logiBUS_exact_70x90.pdf"):
    """Generates a PDF where the paper size (MediaBox) is EXACTLY 70.0 mm x 90.0 mm."""
    out_dir = os.path.dirname(output_pdf)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    card_w = 7.0 * cm
    card_h = 9.0 * cm
    c = canvas.Canvas(output_pdf, pagesize=(card_w, card_h), invariant=1)
    c.setTrimBox((0, 0, card_w, card_h))
    svg_content = generate_card_svg(subapp_file)
    render_card_on_pdf(c, svg_content, 0, 0, card_w, card_h)
    c.showPage()
    c.save()
    print(f"Generated exact 70x90mm PDF: {output_pdf}", flush=True)


def analyze_exercise_layout(
    subapp_file: str,
    resolver: Optional[TypeResolver] = None,
    parser: Optional[NetworkParser] = None,
    settings = None
) -> Tuple[str, str, List[str]]:
    """Analyzes a .SUB file for layout issues relative to the logiBUS card pin layout.

    Returns (exercise_name, subapp_file, list_of_issue_descriptions).
    """
    ex_name = os.path.splitext(os.path.basename(subapp_file))[0]
    if resolver is None:
        type_libs = list(DEFAULT_TYPE_LIBS)
        sub_dir = os.path.dirname(os.path.abspath(subapp_file))
        if sub_dir not in type_libs:
            type_libs.append(sub_dir)
        resolver = TypeResolver(type_libs)
    if parser is None:
        parser = NetworkParser()
    if settings is None:
        settings = load_block_size_settings()

    try:
        model = parser.parse(subapp_file)
        resolver.resolve(model)
        engine = NetworkLayoutEngine(settings=settings)
        engine.layout(model)
    except Exception as e:
        return ex_name, subapp_file, [f"XML-Parse-Fehler: {e}"]

    io_pins = {}     # name -> ('I'/'Q', pin_num, y, x)
    blocks = {}      # name -> (type_name, y, x, inst)
    connections = [] # (src_inst, src_port, dst_inst, dst_port)

    for inst in model.instances:
        pt = identify_passthrough(inst)
        if pt:
            continue
        pin = identify_io_pin(inst)
        if pin:
            if pin.startswith('I') and pin[1:].isdigit():
                io_pins[inst.name] = ('I', int(pin[1:]), inst.y, inst.x)
            elif pin.startswith('AI') and pin[2:].isdigit():
                io_pins[inst.name] = ('I', int(pin[2:]), inst.y, inst.x)
            elif pin.startswith('Q') and pin[1:].isdigit():
                io_pins[inst.name] = ('Q', PinNo(int(pin[1:])), inst.y, inst.x)
        else:
            blocks[inst.name] = (inst.type_name, inst.y, inst.x, inst)

    for conn in model.connections:
        s_parts = conn.source.split('.')
        d_parts = conn.destination.split('.')
        s_inst = s_parts[0]
        s_port = s_parts[1] if len(s_parts) > 1 else ''
        d_inst = d_parts[0]
        d_port = d_parts[1] if len(d_parts) > 1 else ''
        connections.append((s_inst, s_port, d_inst, d_port))

    issues = []
    # 1. IO Pin Ordering in 4diac
    inputs = sorted([(name, info) for name, info in io_pins.items() if info[0] == 'I'], key=lambda x: x[1][1])
    for i in range(len(inputs) - 1):
        for j in range(i + 1, len(inputs)):
            n1, (t1, num1, y1, x1) = inputs[i]
            n2, (t2, num2, y2, x2) = inputs[j]
            if num1 < num2 and y2 < y1 - 100:
                issues.append(f"Pin-Reihenfolge invertiert: Eingang I{num2} (`{n2}`, y={y2:g}) liegt oberhalb von I{num1} (`{n1}`, y={y1:g})")

    outputs = sorted([(name, info) for name, info in io_pins.items() if info[0] == 'Q'], key=lambda x: x[1][1])
    for i in range(len(outputs) - 1):
        for j in range(i + 1, len(outputs)):
            n1, (t1, num1, y1, x1) = outputs[i]
            n2, (t2, num2, y2, x2) = outputs[j]
            if num1 < num2 and y2 < y1 - 100:
                issues.append(f"Pin-Reihenfolge invertiert: Ausgang Q{num2} (`{n2}`, y={y2:g}) liegt oberhalb von Q{num1} (`{n1}`, y={y1:g})")

    # 2. Block placement relative to connected pins
    for blk_name, (blk_type, blk_y, blk_x, b_inst) in blocks.items():
        conn_in_pins = []
        for src_inst, src_port, dst_inst, dst_port in connections:
            if src_inst in io_pins and io_pins[src_inst][0] == 'I' and dst_inst == blk_name:
                conn_in_pins.append((src_inst, io_pins[src_inst]))
        for pin_name, (pt, pnum, py, px) in conn_in_pins:
            for other_blk, (o_type, o_y, o_x, ob_inst) in blocks.items():
                if other_blk == blk_name:
                    continue
                other_conn_pins = [io_pins[s] for s, sp, d, dp in connections if s in io_pins and io_pins[s][0] == 'I' and d == other_blk]
                for (opt, onum, opy, opx) in other_conn_pins:
                    if pnum > onum and blk_y < o_y - 200:
                        issues.append(
                            f"Baustein unglücklich platziert: `{blk_name}` ({blk_type.split('::')[-1]}, verbunden mit I{pnum}) "
                            f"liegt bei y={blk_y:g} oberhalb von `{other_blk}` ({o_type.split('::')[-1]}, verbunden mit I{onum}, y={o_y:g}). "
                            f"Empfehlung: `{blk_name}` in 4diac nach unten verschieben (unterhalb von `{other_blk}`, z.B. y > {o_y:g})."
                        )

    # 3. Same-block input port crossings (e.g. I1 to bottom port, I2 to top port)
    blk_in_conns = {}
    for src_inst, src_port, dst_inst, dst_port in connections:
        if src_inst in io_pins and io_pins[src_inst][0] == 'I' and dst_inst in blocks:
            inst = blocks[dst_inst][3]
            all_in_ports = [p.name for p in inst.event_inputs] + [p.name for p in inst.data_inputs] + [p.name for p in inst.sockets]
            if dst_port in all_in_ports:
                port_idx = all_in_ports.index(dst_port)
                pnum = io_pins[src_inst][1]
                is_event = dst_port in [p.name for p in inst.event_inputs]
                blk_in_conns.setdefault(dst_inst, []).append((pnum, dst_port, port_idx, is_event))

    for blk_name, conns in blk_in_conns.items():
        if len(conns) > 1:
            conns_sorted = sorted(conns, key=lambda x: x[0])
            for i in range(len(conns_sorted) - 1):
                for j in range(i + 1, len(conns_sorted)):
                    p1, port1, idx1, ev1 = conns_sorted[i]
                    p2, port2, idx2, ev2 = conns_sorted[j]
                    # Crossings between an event line and a data line are not worth reporting
                    if ev1 != ev2:
                        continue
                    if p1 < p2 and idx1 > idx2:
                        blk_type = blocks[blk_name][0].split('::')[-1]
                        issues.append(
                            f"Signalleitungen kreuzen sich an `{blk_name}` ({blk_type}): "
                            f"Eingang I{p1} ist mit unterem Port `{port1}` (Position {idx1+1}) verbunden, "
                            f"während I{p2} mit oberem Port `{port2}` (Position {idx2+1}) verbunden ist. "
                            f"Hinweis: Am Baustein liegt `{port1}` unterhalb von `{port2}`, auf der Karte jedoch I{p1} oberhalb von I{p2}. "
                            f"Falls die Pin-Zuordnung der Übung anpassbar ist, empfiehlt sich I{p1} für `{port2}` und I{p2} für `{port1}` "
                            f"für eine kreuzungsfreie Signalführung; andernfalls wird die Kreuzung im Kartengenerator über gestaffelte Kanäle geführt."
                        )

    # 4. Same-block output port crossings (e.g. Q1 to bottom port, Q2 to top port)
    blk_out_conns = {}
    for src_inst, src_port, dst_inst, dst_port in connections:
        if dst_inst in io_pins and io_pins[dst_inst][0] == 'Q' and src_inst in blocks:
            inst = blocks[src_inst][3]
            all_out_ports = [p.name for p in inst.event_outputs] + [p.name for p in inst.data_outputs] + [p.name for p in inst.plugs]
            if src_port in all_out_ports:
                port_idx = all_out_ports.index(src_port)
                pnum = io_pins[dst_inst][1]
                is_event = src_port in [p.name for p in inst.event_outputs]
                blk_out_conns.setdefault(src_inst, []).append((pnum, src_port, port_idx, is_event))

    for blk_name, conns in blk_out_conns.items():
        if len(conns) > 1:
            conns_sorted = sorted(conns, key=lambda x: x[0])
            for i in range(len(conns_sorted) - 1):
                for j in range(i + 1, len(conns_sorted)):
                    p1, port1, idx1, ev1 = conns_sorted[i]
                    p2, port2, idx2, ev2 = conns_sorted[j]
                    # Crossings between an event line and a data line are not worth reporting
                    if ev1 != ev2:
                        continue
                    if p1 < p2 and idx1 > idx2:
                        blk_type = blocks[blk_name][0].split('::')[-1]
                        issues.append(
                            f"Signalleitungen kreuzen sich an `{blk_name}` ({blk_type}): "
                            f"Ausgang Q{p1} ist mit unterem Port `{port1}` (Position {idx1+1}) verbunden, "
                            f"während Q{p2} mit oberem Port `{port2}` (Position {idx2+1}) verbunden ist. "
                            f"Hinweis: Am Baustein liegt `{port1}` unterhalb von `{port2}`, auf der Karte jedoch Q{p1} oberhalb von Q{p2}. "
                            f"Falls die Pin-Zuordnung der Übung anpassbar ist, empfiehlt sich Q{p1} für `{port2}` und Q{p2} für `{port1}` "
                            f"für eine kreuzungsfreie Signalführung; andernfalls wird die Kreuzung im Kartengenerator über gestaffelte Kanäle geführt."
                        )

    issues = list(dict.fromkeys(issues))
    return ex_name, subapp_file, issues


def get_exercise_subfolder(subapp_file: str, configured_folders: Optional[List[str]] = None) -> str:
    """Returns the subfolder name (e.g. 'test_AX' or 'test_B') that this exercise belongs to."""
    if not subapp_file:
        return ""
    norm_file = os.path.normpath(os.path.abspath(subapp_file))
    if configured_folders:
        for f in configured_folders:
            norm_folder = os.path.normpath(os.path.abspath(f))
            if norm_file.startswith(norm_folder):
                return os.path.basename(norm_folder)
    parts = norm_file.split(os.sep)
    for part in parts:
        if part in ("test_AX", "test_B"):
            return part
    return ""


def get_output_paths(subapp_file: str, output_root: str = "output", configured_folders: Optional[List[str]] = None) -> Dict[str, str]:
    """Computes destination directory paths for each variant based on exercise origin folder."""
    subfolder = get_exercise_subfolder(subapp_file, configured_folders)
    base_dir = os.path.join(output_root, subfolder) if subfolder else output_root
    paths = {
        "subfolder": subfolder,
        "base_dir": base_dir,
        "svg": os.path.join(base_dir, "svg"),
        "single": os.path.join(base_dir, "single"),
        "multi": os.path.join(base_dir, "multi"),
        "printshop": os.path.join(base_dir, "printshop"),
        "exact_70x90": os.path.join(base_dir, "exact_70x90"),
    }
    for k, p in paths.items():
        if k != "subfolder" and isinstance(p, str) and p:
            os.makedirs(p, exist_ok=True)
    return paths


def generate_fix_todo_report(subapp_files: List[str], output_path: str = "fix-TODO.md") -> int:
    """Scans subapp files for layout anomalies and writes a formatted fix-TODO.md checklist."""
    type_libs = list(DEFAULT_TYPE_LIBS)
    for f in subapp_files:
        sdir = os.path.dirname(os.path.abspath(f))
        if sdir not in type_libs:
            type_libs.append(sdir)
    resolver = TypeResolver(type_libs)
    parser = NetworkParser()
    settings = load_block_size_settings()

    flagged_by_folder = defaultdict(list)
    total_flagged = 0
    for f in subapp_files:
        res = analyze_exercise_layout(f, resolver=resolver, parser=parser, settings=settings)
        if res and res[2]:
            sfolder = get_exercise_subfolder(f, DEFAULT_EXERCISES_DIRS) or "Weitere"
            flagged_by_folder[sfolder].append(res)
            total_flagged += 1

    lines = [
        "# 4diac Übungs-Layout Fix-TODOs (Karten-Optimierung)",
        "",
        "Dieses Dokument erfasst alle Übungen, bei denen die Platzierung der Bausteine oder IO-Pins im 4diac-Netzwerk nicht der physischen Pin-Reihenfolge des logiBUS® Mini-Trainers entspricht.",
        "",
        "> [!NOTE]",
        "> Auf der physischen Trainingskarte (70 mm × 90 mm) sind die digitalen Eingänge **I1 bis I8 links** fest von oben (1,0 cm) nach unten (8,0 cm) angeordnet, und die Ausgänge **Q1 bis Q8 rechts** von 1,0 cm bis 8,0 cm.",
        "> Wenn in 4diac ein Eingang mit höherer Nummer (z. B. I3) weiter oben gezeichnet ist als ein kleinerer (z. B. I1), ein Baustein unglücklich platziert ist, oder Eingänge an invertierte Anschlusspins am Baustein führen (z. B. I1 an unteren Port und I2 an oberen Port), müssen Verbindungslinien unschön über andere Leitungen kreuzen.",
        "> Sobald die betroffenen FBs oder Anschlüsse in der 4diacIDE angepasst und gespeichert werden, erzeugt der Generator beim nächsten Durchlauf automatisch ein sauberes, kreuzungsfreies Kartenlayout!",
        "",
        "## Übersicht",
        f"- **Geprüfte Übungen:** {len(subapp_files)}",
        f"- **Übungen mit Optimierungsbedarf:** {total_flagged}",
    ]

    for sfolder, f_list in sorted(flagged_by_folder.items()):
        lines.append(f"- **{sfolder}:** {len(f_list)} Übungen")

    lines.extend([
        "",
        "---",
        "",
        "## Offene Layout-TODOs",
        ""
    ])

    for sfolder, f_list in sorted(flagged_by_folder.items()):
        lines.append(f"### {sfolder} ({len(f_list)} Übungen)")
        lines.append("")
        for ex_name, fpath, issues in f_list:
            rel_path = os.path.relpath(fpath, os.getcwd()) if os.path.isabs(fpath) else fpath
            rel_path = rel_path.replace("\\", "/")
            lines.append(f"- [ ] **{ex_name}** (`{rel_path}`)")
            for iss in issues:
                lines.append(f"  - {iss}")
            lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return total_flagged


def find_sub_files(folders: List[str]) -> List[str]:
    """Finds all .SUB exercise files from a list of folders, checking both
    direct files (*.SUB) and exercise subdirectories (Uebungen/*.SUB).
    Deduplicates and returns sorted paths.
    """
    found = []
    seen = set()
    for f in folders:
        candidates = [
            os.path.join(f, "*.SUB"),
            os.path.join(f, "Uebungen", "*.SUB"),
        ]
        for pattern in candidates:
            for fpath in glob.glob(pattern):
                norm = os.path.normpath(os.path.abspath(fpath))
                if norm not in seen:
                    seen.add(norm)
                    found.append(norm)
    return sorted(found)


def resolve_sub_file(sub_arg: str, folders: List[str]) -> str:
    """Resolves an exercise file path, which can be an absolute path,
    a relative path, or just a filename (with or without .SUB extension)
    located in one of the configured folders or their Uebungen subdirectories.
    """
    if os.path.isabs(sub_arg) and os.path.exists(sub_arg):
        return sub_arg
    if os.path.exists(sub_arg):
        return os.path.abspath(sub_arg)

    for f in folders:
        for candidate in [
            os.path.join(f, sub_arg),
            os.path.join(f, f"{sub_arg}.SUB"),
            os.path.join(f, "Uebungen", sub_arg),
            os.path.join(f, "Uebungen", f"{sub_arg}.SUB"),
        ]:
            if os.path.exists(candidate):
                return os.path.abspath(candidate)
    return sub_arg


def main():
    arg_parser = argparse.ArgumentParser(description="Generate 7x9cm portrait training cards from 4diac exercises.")
    arg_parser.add_argument("--sub", type=str, default=DEFAULT_EXERCISE, help="Path to .SUB exercise file")
    arg_parser.add_argument("--all", action="store_true", help="Generate multi-card PDF for all exercises in folder")
    arg_parser.add_argument("--batch-all", action="store_true", help="Generate all card variants for every exercise in folder")
    arg_parser.add_argument("--check-layout", action="store_true", help="Analyze exercise layouts and generate fix-TODO.md")
    arg_parser.add_argument("--limit", type=int, default=None, help="Limit number of exercises to process (useful for testing)")
    arg_parser.add_argument(
        "--folder", "--folders",
        dest="folders",
        type=str,
        nargs="+",
        default=DEFAULT_EXERCISES_DIRS,
        help="One or more folders containing .SUB files or exercise subdirectories (default: test_AX and test_B)"
    )
    arg_parser.add_argument("--output-dir", type=str, default="output", help="Root output directory (default: 'output')")
    arg_parser.add_argument("--single-out", type=str, default=None, help="Custom output path for single card PDF")
    arg_parser.add_argument("--multi-out", type=str, default=None, help="Custom output path for multi card PDF")
    arg_parser.add_argument("--printshop-out", type=str, default=None, help="Custom output path for print shop offset PDF")
    arg_parser.add_argument("--exact-out", type=str, default=None, help="Custom output path for exact 70x90mm PDF")
    arg_parser.add_argument("--svg-out", type=str, default=None, help="Custom output path for standalone SVG")
    arg_parser.add_argument("--todo-out", type=str, default="fix-TODO.md", help="Path to output fix-TODO.md file")
    args = arg_parser.parse_args()

    if args.check_layout:
        files = find_sub_files(args.folders)
        if args.limit and args.limit > 0:
            files = files[:args.limit]
        folders_desc = ", ".join(args.folders)
        print(f"Analysiere Layout von {len(files)} Übungen in {folders_desc}...", flush=True)
        if not files:
            print("[LAYOUT-CHECK] Keine Übungen gefunden. Report wird nicht geschrieben.", flush=True)
            return
        if args.limit and args.todo_out == "fix-TODO.md":
            print(f"[LAYOUT-CHECK] Hinweis: Testlauf mit --limit={args.limit}. 'fix-TODO.md' wird nicht überschrieben (nutze ggf. --todo-out).", flush=True)
            return
        count = generate_fix_todo_report(files, args.todo_out)
        print(f"[LAYOUT-CHECK] Fertig: {count} Übungen mit Optimierungsbedarf in '{args.todo_out}' dokumentiert.", flush=True)
        return

    output_root = args.output_dir

    if args.batch_all:
        files = find_sub_files(args.folders)
        if args.limit and args.limit > 0:
            files = files[:args.limit]
        print(f"Batch generating cards for {len(files)} exercises across {len(args.folders)} folders into '{output_root}'...", flush=True)

        files_by_folder = defaultdict(list)
        for i, fpath in enumerate(files):
            b_name = os.path.splitext(os.path.basename(fpath))[0]
            out_paths = get_output_paths(fpath, output_root, args.folders)
            subfolder = out_paths["subfolder"]
            files_by_folder[subfolder].append(fpath)

            print(f"[{i+1}/{len(files)}] [{subfolder or 'default'}] Processing {b_name}...", flush=True)
            try:
                svg_content = generate_card_svg(fpath)
                with open(os.path.join(out_paths["svg"], f"{b_name}_card.svg"), "w", encoding="utf-8") as f:
                    f.write(svg_content)
                generate_single_card_pdf(fpath, os.path.join(out_paths["single"], f"{b_name}_single.pdf"))
                generate_printshop_pdf(fpath, os.path.join(out_paths["printshop"], f"{b_name}_printshop.pdf"))
                generate_exact_size_pdf(fpath, os.path.join(out_paths["exact_70x90"], f"{b_name}_exact_70x90.pdf"))
            except Exception as e:
                print(f"  [WARNUNG] Fehler bei {b_name}: {e}", flush=True)

        # Generate multi-card PDFs per folder
        for sfolder, folder_files in files_by_folder.items():
            folder_base = os.path.join(output_root, sfolder) if sfolder else output_root
            folder_multi_dir = os.path.join(folder_base, "multi")
            os.makedirs(folder_multi_dir, exist_ok=True)
            multi_name = f"{sfolder}_all_exercises_multi.pdf" if sfolder else "all_exercises_multi.pdf"
            multi_out = args.multi_out or os.path.join(folder_multi_dir, multi_name)
            print(f"Generating multi-card PDF for {len(folder_files)} exercises in '{sfolder or 'default'}': {multi_out}...", flush=True)
            generate_multi_cards_pdf(folder_files, multi_out)

        # Generate fix-TODO.md
        if not args.limit and files:
            print("Erstelle Layout-Analyse (fix-TODO.md)...", flush=True)
            count = generate_fix_todo_report(files, args.todo_out)
            print(f"[LAYOUT-CHECK] {count} Übungen mit Optimierungsbedarf in '{args.todo_out}' dokumentiert.", flush=True)
        elif args.limit:
            print(f"[LAYOUT-CHECK] Hinweis: Testlauf mit --limit={args.limit}. '{args.todo_out}' wird nicht überschrieben.", flush=True)

    elif args.all:
        files = find_sub_files(args.folders)
        if args.limit and args.limit > 0:
            files = files[:args.limit]
        print(f"Found {len(files)} exercises across {len(args.folders)} folders", flush=True)

        files_by_folder = defaultdict(list)
        for fpath in files:
            subfolder = get_exercise_subfolder(fpath, args.folders)
            files_by_folder[subfolder].append(fpath)

        for sfolder, folder_files in files_by_folder.items():
            folder_base = os.path.join(output_root, sfolder) if sfolder else output_root
            folder_multi_dir = os.path.join(folder_base, "multi")
            os.makedirs(folder_multi_dir, exist_ok=True)
            multi_name = f"{sfolder}_all_exercises_multi.pdf" if sfolder else "all_exercises_multi.pdf"
            multi_out = os.path.join(folder_multi_dir, multi_name)
            print(f"Generating multi-card PDF for {len(folder_files)} exercises in '{sfolder or 'default'}': {multi_out}...", flush=True)
            generate_multi_cards_pdf(folder_files, multi_out)

            if folder_files:
                first_file = folder_files[0]
                first_base = os.path.splitext(os.path.basename(first_file))[0]
                out_paths = get_output_paths(first_file, output_root, args.folders)

                svg_out = os.path.join(out_paths["svg"], f"{first_base}_card.svg")
                svg_content = generate_card_svg(first_file)
                with open(svg_out, "w", encoding="utf-8") as f:
                    f.write(svg_content)
                print(f"Saved SVG: {svg_out}", flush=True)

                single_out = os.path.join(out_paths["single"], f"{first_base}_single.pdf")
                generate_single_card_pdf(first_file, single_out)

                printshop_out = os.path.join(out_paths["printshop"], f"{first_base}_printshop.pdf")
                generate_printshop_pdf(first_file, printshop_out)

                exact_out = os.path.join(out_paths["exact_70x90"], f"{first_base}_exact_70x90.pdf")
                generate_exact_size_pdf(first_file, exact_out)

        # Generate fix-TODO.md
        if not args.limit and files:
            print("Erstelle Layout-Analyse (fix-TODO.md)...", flush=True)
            count = generate_fix_todo_report(files, args.todo_out)
            print(f"[LAYOUT-CHECK] {count} Übungen mit Optimierungsbedarf in '{args.todo_out}' dokumentiert.", flush=True)
        elif args.limit:
            print(f"[LAYOUT-CHECK] Hinweis: Testlauf mit --limit={args.limit}. '{args.todo_out}' wird nicht überschrieben.", flush=True)

    else:
        target_sub = resolve_sub_file(args.sub, args.folders)

        print(f"Processing exercise: {target_sub}", flush=True)
        base_name = os.path.splitext(os.path.basename(target_sub))[0]

        # Check layout and notify
        res = analyze_exercise_layout(target_sub)
        if res and res[2]:
            print(f"\n[LAYOUT-HINWEIS] {len(res[2])} Optimierungshinweise für {base_name}:", flush=True)
            for iss in res[2]:
                print(f"  * {iss}", flush=True)
            print(f"  (Detaillierte Liste aller Übungen siehe auch '{args.todo_out}')\n", flush=True)

        out_paths = get_output_paths(target_sub, output_root, args.folders)

        # Standalone SVG
        svg_out = args.svg_out or os.path.join(out_paths["svg"], f"{base_name}_card.svg")
        svg_content = generate_card_svg(target_sub)
        with open(svg_out, "w", encoding="utf-8") as f:
            f.write(svg_content)
        print(f"Saved SVG: {svg_out}", flush=True)

        # Variant 1: Single card on DIN A4
        single_out = args.single_out or os.path.join(out_paths["single"], f"{base_name}_single.pdf")
        generate_single_card_pdf(target_sub, single_out)

        # Variant 2: Multi card sheet (6 cards on A4)
        multi_out = args.multi_out or os.path.join(out_paths["multi"], f"{base_name}_multi.pdf")
        multi_list = [target_sub] * 6
        generate_multi_cards_pdf(multi_list, multi_out)

        # Variant 3: Print shop offset PDF (TrimBox=70x90mm, crop marks outside)
        printshop_out = args.printshop_out or os.path.join(out_paths["printshop"], f"{base_name}_printshop.pdf")
        generate_printshop_pdf(target_sub, printshop_out)

        # Variant 3b: Print shop exact 70x90mm PDF (MediaBox=70x90mm)
        exact_out = args.exact_out or os.path.join(out_paths["exact_70x90"], f"{base_name}_exact_70x90.pdf")
        generate_exact_size_pdf(target_sub, exact_out)

    print("Generation complete!", flush=True)


if __name__ == "__main__":
    main()

