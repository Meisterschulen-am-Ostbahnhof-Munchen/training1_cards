import json
import sys

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm, mm
    from reportlab.pdfgen import canvas
except ModuleNotFoundError:
    print("=" * 80)
    print("FEHLER: Die Bibliothek 'reportlab' ist nicht installiert.")
    print("Bitte installiere ReportLab mit folgendem Befehl, um die Karten zu generieren:")
    print("    pip install reportlab")
    print("=" * 80)
    sys.exit(1)

def draw_crop_marks(c, x, y, w, h, length=0.6*cm, offset=0.15*cm):
    """Draws professional crop marks at the corners of a card."""
    c.setStrokeColor(colors.HexColor('#7F8C8D'))
    c.setLineWidth(0.3)
    
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

def draw_badge(c, bx, by, text, badge_type="input"):
    """Draws a beautiful rounded badge for input/output terminals."""
    w = 0.5 * cm
    h = 0.28 * cm
    
    if badge_type == "input":
        bg_color = colors.HexColor('#27AE60')  # Green for Inputs
    else:
        bg_color = colors.HexColor('#2980B9')  # Blue for Outputs
        
    c.setFillColor(bg_color)
    c.setStrokeColor(bg_color)
    c.roundRect(bx - w/2, by - h/2, w, h, 0.06*cm, fill=True, stroke=True)
    
    # Text inside badge
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 6.0)
    c.drawCentredString(bx, by - 2, text)

def draw_switch_icon(c, sx, sy, position="left"):
    """Draws a tiny slide switch symbol on the card showing knob on the left/right."""
    # Outer frame
    c.setStrokeColor(colors.HexColor('#7F8C8D'))
    c.setFillColor(colors.white)
    c.setLineWidth(0.5)
    sw_w = 0.22 * cm
    sw_h = 0.12 * cm
    c.rect(sx - sw_w/2, sy - sw_h/2, sw_w, sw_h, fill=True, stroke=True)
    
    # Switch slider knob
    c.setFillColor(colors.HexColor('#2C3E50'))  # Dark blue knob
    knob_w = 0.1 * cm
    knob_h = 0.09 * cm
    if position == "left":
        c.rect(sx - sw_w/2 + 0.015*cm, sy - knob_h/2, knob_w, knob_h, fill=True, stroke=False)
    else:
        c.rect(sx + sw_w/2 - knob_w - 0.015*cm, sy - knob_h/2, knob_w, knob_h, fill=True, stroke=False)

def draw_corner_boxes(c, x, y, task, card_w, card_h):
    """Draws beautiful styled corner info badges for exercise number and branding."""
    # Left Corner Box (Exercise number)
    box_x = x + 0.08 * cm
    box_y = y + 0.5 * cm
    box_w = 0.56 * cm
    box_h = 0.22 * cm
    
    c.setFillColor(colors.HexColor('#F2F4F4'))  # Very light grey
    c.setStrokeColor(colors.HexColor('#BDC3C7'))
    c.setLineWidth(0.4)
    c.roundRect(box_x, box_y, box_w, box_h, 0.04*cm, fill=True, stroke=True)
    
    c.setFillColor(colors.HexColor('#2C3E50'))
    c.setFont("Helvetica-Bold", 4.5)
    c.drawCentredString(box_x + box_w/2.0, box_y + box_h/2.0 - 1.5, f"U{task.get('id', '')}")
    
    # Right Corner Box (Branding)
    rbox_x = x + card_w - 0.72 * cm
    rbox_y = y + 0.5 * cm
    rbox_w = 0.64 * cm
    rbox_h = 0.54 * cm
    
    c.setFillColor(colors.HexColor('#EBF5FB'))  # Light blue
    c.setStrokeColor(colors.HexColor('#AED6F1'))
    c.setLineWidth(0.4)
    c.roundRect(rbox_x, rbox_y, rbox_w, rbox_h, 0.04*cm, fill=True, stroke=True)
    
    c.setFont("Helvetica-Bold", 3.5)
    c.setFillColor(colors.HexColor('#2980B9'))
    c.drawCentredString(rbox_x + rbox_w/2.0, rbox_y + 0.38*cm, "logiBUS")
    c.drawCentredString(rbox_x + rbox_w/2.0, rbox_y + 0.26*cm, "Mini")
    c.drawCentredString(rbox_x + rbox_w/2.0, rbox_y + 0.14*cm, "Trainer")
    c.setFont("Helvetica-Bold", 2.8)
    c.setFillColor(colors.HexColor('#7F8C8D'))
    c.drawCentredString(rbox_x + rbox_w/2.0, rbox_y + 0.04*cm, "4diac\u2122")

# --- VECTOR GRAPHICS DRAWING FUNCTIONS ---

def draw_garage_door(c, cx, cy):
    """Draws a garage door simulation vector graphic."""
    # Garage body
    c.setFillColor(colors.HexColor('#ECF0F1'))
    c.setStrokeColor(colors.HexColor('#7F8C8D'))
    c.setLineWidth(0.8)
    c.rect(cx - 0.9*cm, cy - 0.8*cm, 1.8*cm, 1.5*cm, fill=True, stroke=True)
    
    # Roof (Triangular)
    p = c.beginPath()
    p.moveTo(cx - 1.0*cm, cy + 0.7*cm)
    p.lineTo(cx, cy + 1.2*cm)
    p.lineTo(cx + 1.0*cm, cy + 0.7*cm)
    p.close()
    c.setFillColor(colors.HexColor('#E74C3C'))
    c.drawPath(p, fill=True, stroke=True)
    
    # Door frame/opening
    c.setFillColor(colors.HexColor('#BDC3C7'))
    c.rect(cx - 0.6*cm, cy - 0.8*cm, 1.2*cm, 1.2*cm, fill=True, stroke=True)
    
    # Rolling door slats
    c.setStrokeColor(colors.HexColor('#95A5A6'))
    c.setLineWidth(0.6)
    for sy in range(1, 11):
        y_pos = cy - 0.8*cm + sy*0.11*cm
        c.line(cx - 0.6*cm, y_pos, cx + 0.6*cm, y_pos)
        
    # Flashing light
    c.setFillColor(colors.HexColor('#E67E22'))
    c.circle(cx - 0.6*cm, cy + 0.9*cm, 0.1*cm, fill=True, stroke=True)
    
    # Direction arrow
    c.setStrokeColor(colors.HexColor('#2980B9'))
    c.setLineWidth(1.0)
    c.line(cx + 1.05*cm, cy - 0.3*cm, cx + 1.05*cm, cy + 0.3*cm)
    c.line(cx + 0.97*cm, cy + 0.15*cm, cx + 1.05*cm, cy + 0.3*cm)
    c.line(cx + 1.13*cm, cy + 0.15*cm, cx + 1.05*cm, cy + 0.3*cm)

def draw_mixer_tank(c, cx, cy):
    """Draws a chemical mixer tank vector graphic."""
    # Tank outline
    c.setFillColor(colors.HexColor('#ECF0F1'))
    c.setStrokeColor(colors.HexColor('#7F8C8D'))
    c.setLineWidth(0.8)
    c.roundRect(cx - 0.6*cm, cy - 0.8*cm, 1.2*cm, 1.6*cm, 0.12*cm, fill=True, stroke=True)
    
    # Water level
    c.setFillColor(colors.HexColor('#3498DB'))
    c.roundRect(cx - 0.56*cm, cy - 0.8*cm, 1.12*cm, 1.0*cm, 0.08*cm, fill=True, stroke=False)
    
    # Re-stroke tank border
    c.setStrokeColor(colors.HexColor('#7F8C8D'))
    c.setFillColor(colors.transparent)
    c.roundRect(cx - 0.6*cm, cy - 0.8*cm, 1.2*cm, 1.6*cm, 0.12*cm, fill=False, stroke=True)
    
    # Mixer Motor & Shaft
    c.setFillColor(colors.HexColor('#34495E'))
    c.rect(cx - 0.2*cm, cy + 0.8*cm, 0.4*cm, 0.25*cm, fill=True, stroke=True)
    c.setStrokeColor(colors.HexColor('#2C3E50'))
    c.setLineWidth(1.0)
    c.line(cx, cy + 0.8*cm, cx, cy - 0.4*cm)
    
    # Stirrer blades
    c.rect(cx - 0.4*cm, cy - 0.4*cm, 0.8*cm, 0.12*cm, fill=True, stroke=True)
    c.rect(cx - 0.25*cm, cy - 0.15*cm, 0.5*cm, 0.08*cm, fill=True, stroke=True)
    
    # Pipes
    c.setStrokeColor(colors.HexColor('#7F8C8D'))
    c.setLineWidth(1.5)
    c.line(cx - 0.9*cm, cy + 0.5*cm, cx - 0.6*cm, cy + 0.5*cm)
    c.line(cx + 0.6*cm, cy - 0.6*cm, cx + 0.9*cm, cy - 0.6*cm)
    
    # Level indicators
    c.setFillColor(colors.HexColor('#E74C3C'))
    c.circle(cx + 0.6*cm, cy + 0.2*cm, 0.06*cm, fill=True, stroke=False)
    c.circle(cx + 0.6*cm, cy - 0.5*cm, 0.06*cm, fill=True, stroke=False)

def draw_traffic_light(c, cx, cy):
    """Draws a traffic light vector graphic."""
    # Mast
    c.setFillColor(colors.HexColor('#7F8C8D'))
    c.rect(cx - 0.06*cm, cy - 1.1*cm, 0.12*cm, 0.4*cm, fill=True, stroke=False)
    
    # Housing
    c.setFillColor(colors.HexColor('#2C3E50'))
    c.setStrokeColor(colors.HexColor('#34495E'))
    c.setLineWidth(0.8)
    c.roundRect(cx - 0.38*cm, cy - 0.7*cm, 0.76*cm, 1.5*cm, 0.1*cm, fill=True, stroke=True)
    
    # Lights
    c.setFillColor(colors.HexColor('#E74C3C'))
    c.circle(cx, cy + 0.38*cm, 0.18*cm, fill=True, stroke=True)
    c.setFillColor(colors.HexColor('#F1C40F'))
    c.circle(cx, cy, 0.18*cm, fill=True, stroke=True)
    c.setFillColor(colors.HexColor('#2ECC71'))
    c.circle(cx, cy - 0.38*cm, 0.18*cm, fill=True, stroke=True)

def draw_conveyor_belt(c, cx, cy):
    """Draws a conveyor belt vector graphic."""
    # Wheels
    c.setFillColor(colors.HexColor('#7F8C8D'))
    c.setStrokeColor(colors.HexColor('#34495E'))
    c.setLineWidth(0.8)
    c.circle(cx - 0.7*cm, cy - 0.3*cm, 0.18*cm, fill=True, stroke=True)
    c.circle(cx + 0.7*cm, cy - 0.3*cm, 0.18*cm, fill=True, stroke=True)
    
    # Loop
    c.setStrokeColor(colors.HexColor('#34495E'))
    c.setLineWidth(1.0)
    c.roundRect(cx - 0.9*cm, cy - 0.48*cm, 1.8*cm, 0.36*cm, 0.18*cm, fill=False, stroke=True)
    
    # Box
    c.setFillColor(colors.HexColor('#D35400'))
    c.setStrokeColor(colors.HexColor('#A04000'))
    c.rect(cx - 0.3*cm, cy - 0.12*cm, 0.6*cm, 0.4*cm, fill=True, stroke=True)
    
    # Tape
    c.setStrokeColor(colors.HexColor('#F39C12'))
    c.setLineWidth(0.6)
    c.line(cx, cy - 0.12*cm, cx, cy + 0.28*cm)
    
    # Arrow
    c.setStrokeColor(colors.HexColor('#27AE60'))
    c.setLineWidth(1.0)
    c.line(cx - 0.3*cm, cy + 0.45*cm, cx + 0.3*cm, cy + 0.45*cm)
    c.line(cx + 0.18*cm, cy + 0.38*cm, cx + 0.3*cm, cy + 0.45*cm)
    c.line(cx + 0.18*cm, cy + 0.52*cm, cx + 0.3*cm, cy + 0.45*cm)

def draw_default_logic(c, cx, cy):
    """Draws a standard SR Flip-Flop function block as a fallback."""
    c.setFillColor(colors.HexColor('#F8F9F9'))
    c.setStrokeColor(colors.HexColor('#2C3E50'))
    c.setLineWidth(0.8)
    c.rect(cx - 0.5*cm, cy - 0.7*cm, 1.0*cm, 1.4*cm, fill=True, stroke=True)
    
    # Title
    c.setFillColor(colors.HexColor('#2C3E50'))
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(cx, cy + 0.35*cm, "SR")
    
    # Inputs
    c.setFont("Helvetica", 5.0)
    c.drawString(cx - 0.4*cm, cy + 0.05*cm, "S")
    c.drawString(cx - 0.4*cm, cy - 0.35*cm, "R")
    c.line(cx - 0.8*cm, cy + 0.1*cm, cx - 0.5*cm, cy + 0.1*cm)
    c.line(cx - 0.8*cm, cy - 0.3*cm, cx - 0.5*cm, cy - 0.3*cm)
    
    # Output
    c.drawRightString(cx + 0.4*cm, cy + 0.05*cm, "Q")
    c.line(cx + 0.5*cm, cy + 0.1*cm, cx + 0.8*cm, cy + 0.1*cm)

# --- SCHEMATIC CONNECTION LINES ROUTER ---

def draw_task_connections(c, x, y, task):
    """Draws lines from bottom/top pins to the center graphic box, with vertical labels."""
    inputs = task.get("inputs", {})
    outputs = task.get("outputs", {})
    
    # Graphic bounding box
    g_left = x + 3.0 * cm
    g_right = x + 6.0 * cm
    g_bottom = y + 2.0 * cm
    g_top = y + 5.0 * cm
    
    # Start/End constraints to prevent drawing over badge boxes
    start_y = y + 0.44 * cm
    end_y = y + 6.56 * cm
    
    c.setStrokeColor(colors.HexColor('#2C3E50'))
    c.setLineWidth(0.6)
    
    # Draw inputs connections
    for k, label in inputs.items():
        if not k.startswith("I") or not k[1:].isdigit():
            continue
        i = int(k[1:])
        px = x + i * cm
        
        # Connect segment from border to badge
        c.line(px, y, px, y + 0.16*cm)
        
        if i < 3:  # I1, I2 -> go up and right
            target_y = y + 2.3 * cm + (i - 1) * 0.4 * cm
            c.line(px, start_y, px, target_y)
            c.line(px, target_y, g_left, target_y)
            
            # Label (shifted horizontally to the right of the line, preventing overlaps)
            c.saveState()
            c.setFillColor(colors.HexColor('#7F8C8D'))
            c.setFont("Helvetica-Bold", 4.5)
            c.translate(px + 0.22*cm, y + 0.55*cm)
            c.rotate(90)
            c.drawString(0, 0, label)
            c.restoreState()
            
        elif i > 6:  # I7, I8 -> go up and left
            target_y = y + 2.3 * cm + (8 - i) * 0.4 * cm
            c.line(px, start_y, px, target_y)
            c.line(px, target_y, g_right, target_y)
            
            # Label
            c.saveState()
            c.setFillColor(colors.HexColor('#7F8C8D'))
            c.setFont("Helvetica-Bold", 4.5)
            c.translate(px + 0.22*cm, y + 0.55*cm)
            c.rotate(90)
            c.drawString(0, 0, label)
            c.restoreState()
            
        else:  # I3, I4, I5, I6 -> go straight up
            c.line(px, start_y, px, g_bottom)
            
            # Label
            c.saveState()
            c.setFillColor(colors.HexColor('#7F8C8D'))
            c.setFont("Helvetica-Bold", 4.5)
            c.translate(px + 0.22*cm, y + 0.55*cm)
            c.rotate(90)
            c.drawString(0, 0, label)
            c.restoreState()

    # Draw outputs connections
    for k, label in outputs.items():
        if not k.startswith("Q") or not k[1:].isdigit():
            continue
        i = int(k[1:])
        px = x + i * cm
        
        # Connect segment from border to badge
        c.line(px, y + 7.0*cm, px, y + 6.84*cm)
        
        if i < 3:  # Q1, Q2 -> go down and right
            target_y = y + 4.7 * cm - (i - 1) * 0.4 * cm
            c.line(px, end_y, px, target_y)
            c.line(px, target_y, g_left, target_y)
            
            # Label (shifted horizontally to the left of the line, preventing overlaps)
            c.saveState()
            c.setFillColor(colors.HexColor('#7F8C8D'))
            c.setFont("Helvetica-Bold", 4.5)
            c.translate(px - 0.12*cm, y + 6.45*cm)
            c.rotate(90)
            c.drawRightString(0, 0, label)
            c.restoreState()
            
        elif i > 6:  # Q7, Q8 -> go down and left
            target_y = y + 4.7 * cm - (8 - i) * 0.4 * cm
            c.line(px, end_y, px, target_y)
            c.line(px, target_y, g_right, target_y)
            
            # Label
            c.saveState()
            c.setFillColor(colors.HexColor('#7F8C8D'))
            c.setFont("Helvetica-Bold", 4.5)
            c.translate(px - 0.12*cm, y + 6.45*cm)
            c.rotate(90)
            c.drawRightString(0, 0, label)
            c.restoreState()
            
        else:  # Q3, Q4, Q5, Q6 -> go straight down
            c.line(px, end_y, px, g_top)
            
            # Label
            c.saveState()
            c.setFillColor(colors.HexColor('#7F8C8D'))
            c.setFont("Helvetica-Bold", 4.5)
            c.translate(px - 0.12*cm, y + 6.45*cm)
            c.rotate(90)
            c.drawRightString(0, 0, label)
            c.restoreState()

def draw_logic_gates(c, x, y):
    """Draws the AND, OR, NOT logic gate schematic matching TC100, docking directly to pins."""
    c.setStrokeColor(colors.HexColor('#2C3E50'))
    c.setLineWidth(0.8)
    
    # Gate positions
    and_x = x + 3.0 * cm
    or_x = x + 5.0 * cm
    not_x = x + 7.5 * cm
    cy = y + 3.5 * cm
    
    # Draw gates
    # AND gate
    and_w = 0.5 * cm
    and_h = 0.75 * cm
    c.setFillColor(colors.HexColor('#FDF2E9'))  # light orange
    c.setStrokeColor(colors.HexColor('#E67E22'))
    c.rect(and_x - and_w/2, cy - and_h/2, and_w, and_h, fill=True, stroke=True)
    c.setFillColor(colors.HexColor('#D35400'))
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(and_x, cy - 2.5, "&")
    
    # OR gate
    or_w = 0.5 * cm
    or_h = 0.75 * cm
    c.setFillColor(colors.HexColor('#FDF2E9'))
    c.setStrokeColor(colors.HexColor('#E67E22'))
    c.rect(or_x - or_w/2, cy - or_h/2, or_w, or_h, fill=True, stroke=True)
    c.setFillColor(colors.HexColor('#D35400'))
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(or_x, cy - 3.0, ">=1")
    
    # NOT gate
    not_w = 0.5 * cm
    not_h = 0.75 * cm
    c.setFillColor(colors.HexColor('#FDF2E9'))
    c.setStrokeColor(colors.HexColor('#E67E22'))
    c.rect(not_x - not_w/2, cy - not_h/2, not_w, not_h, fill=True, stroke=True)
    c.setFillColor(colors.HexColor('#D35400'))
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(not_x, cy - 2.5, "1")
    
    # NOT inversion bubble on output
    bubble_r = 0.05 * cm
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.HexColor('#E67E22'))
    c.circle(not_x + not_w/2 + bubble_r, cy, bubble_r, fill=True, stroke=True)
    
    # Start/End constraints to prevent drawing over badge boxes
    start_y = y + 0.44 * cm
    end_y = y + 6.56 * cm
    
    # Draw connections
    c.setStrokeColor(colors.HexColor('#2C3E50'))
    c.setLineWidth(0.6)
    
    # AND connection lines (I1 at 1cm, I2 at 2cm -> AND; output -> Q1 at 1cm)
    c.line(x + 1.0*cm, y, x + 1.0*cm, y + 0.16*cm) # line segment under badge
    c.line(x + 1.0*cm, start_y, x + 1.0*cm, cy + 0.15*cm)
    c.line(x + 1.0*cm, cy + 0.15*cm, and_x - and_w/2, cy + 0.15*cm)
    
    c.line(x + 2.0*cm, y, x + 2.0*cm, y + 0.16*cm) # line segment under badge
    c.line(x + 2.0*cm, start_y, x + 2.0*cm, cy - 0.15*cm)
    c.line(x + 2.0*cm, cy - 0.15*cm, and_x - and_w/2, cy - 0.15*cm)
    
    c.line(and_x + and_w/2, cy, and_x + 0.4*cm, cy)
    c.line(and_x + 0.4*cm, cy, and_x + 0.4*cm, cy + 0.7*cm)
    c.line(and_x + 0.4*cm, cy + 0.7*cm, x + 1.0*cm, cy + 0.7*cm)
    c.line(x + 1.0*cm, cy + 0.7*cm, x + 1.0*cm, end_y)
    c.line(x + 1.0*cm, y + 7.0*cm, x + 1.0*cm, y + 6.84*cm) # line segment above badge
    
    # OR connection lines (I4 at 4cm, I5 at 5cm -> OR; output -> Q2 at 2cm)
    c.line(x + 4.0*cm, y, x + 4.0*cm, y + 0.16*cm) # line segment under badge
    c.line(x + 4.0*cm, start_y, x + 4.0*cm, cy + 0.15*cm)
    c.line(x + 4.0*cm, cy + 0.15*cm, or_x - or_w/2, cy + 0.15*cm)
    
    c.line(x + 5.0*cm, y, x + 5.0*cm, y + 0.16*cm) # line segment under badge
    c.line(x + 5.0*cm, start_y, x + 5.0*cm, cy - 0.15*cm)
    c.line(x + 5.0*cm, cy - 0.15*cm, or_x - or_w/2, cy - 0.15*cm)
    
    c.line(or_x + or_w/2, cy, or_x + 0.4*cm, cy)
    c.line(or_x + 0.4*cm, cy, or_x + 0.4*cm, cy + 1.1*cm)
    c.line(or_x + 0.4*cm, cy + 1.1*cm, x + 2.0*cm, cy + 1.1*cm)
    c.line(x + 2.0*cm, cy + 1.1*cm, x + 2.0*cm, end_y)
    c.line(x + 2.0*cm, y + 7.0*cm, x + 2.0*cm, y + 6.84*cm) # line segment above badge
    
    # NOT connection lines (I7 at 7cm -> NOT; output -> Q3 at 3cm)
    c.line(x + 7.0*cm, y, x + 7.0*cm, y + 0.16*cm) # line segment under badge
    c.line(x + 7.0*cm, start_y, x + 7.0*cm, cy)
    c.line(x + 7.0*cm, cy, not_x - not_w/2, cy)
    
    c.line(not_x + not_w/2 + 2*bubble_r, cy, not_x + 0.4*cm, cy)
    c.line(not_x + 0.4*cm, cy, not_x + 0.4*cm, cy + 1.5*cm)
    c.line(not_x + 0.4*cm, cy + 1.5*cm, x + 3.0*cm, cy + 1.5*cm)
    c.line(x + 3.0*cm, cy + 1.5*cm, x + 3.0*cm, end_y)
    c.line(x + 3.0*cm, y + 7.0*cm, x + 3.0*cm, y + 6.84*cm) # line segment above badge

    # Print labels vertically next to lines (shifted horizontally to prevent overlaying)
    # I1 label
    c.saveState()
    c.setFillColor(colors.HexColor('#7F8C8D'))
    c.setFont("Helvetica-Bold", 4.5)
    c.translate(x + 1.0*cm + 0.22*cm, y + 0.55*cm)
    c.rotate(90)
    c.drawString(0, 0, "Und-Eingang 1")
    c.restoreState()
    
    # I2 label
    c.saveState()
    c.setFillColor(colors.HexColor('#7F8C8D'))
    c.setFont("Helvetica-Bold", 4.5)
    c.translate(x + 2.0*cm + 0.22*cm, y + 0.55*cm)
    c.rotate(90)
    c.drawString(0, 0, "Und-Eingang 2")
    c.restoreState()
    
    # I4 label
    c.saveState()
    c.setFillColor(colors.HexColor('#7F8C8D'))
    c.setFont("Helvetica-Bold", 4.5)
    c.translate(x + 4.0*cm + 0.22*cm, y + 0.55*cm)
    c.rotate(90)
    c.drawString(0, 0, "Oder-Eingang 1")
    c.restoreState()
    
    # I5 label
    c.saveState()
    c.setFillColor(colors.HexColor('#7F8C8D'))
    c.setFont("Helvetica-Bold", 4.5)
    c.translate(x + 5.0*cm + 0.22*cm, y + 0.55*cm)
    c.rotate(90)
    c.drawString(0, 0, "Oder-Eingang 2")
    c.restoreState()
    
    # I7 label
    c.saveState()
    c.setFillColor(colors.HexColor('#7F8C8D'))
    c.setFont("Helvetica-Bold", 4.5)
    c.translate(x + 7.0*cm + 0.22*cm, y + 0.55*cm)
    c.rotate(90)
    c.drawString(0, 0, "Nicht-Eingang")
    c.restoreState()
    
    # Q1 label
    c.saveState()
    c.setFillColor(colors.HexColor('#7F8C8D'))
    c.setFont("Helvetica-Bold", 4.5)
    c.translate(x + 1.0*cm - 0.12*cm, y + 6.45*cm)
    c.rotate(90)
    c.drawRightString(0, 0, "Ausgang AND")
    c.restoreState()
    
    # Q2 label
    c.saveState()
    c.setFillColor(colors.HexColor('#7F8C8D'))
    c.setFont("Helvetica-Bold", 4.5)
    c.translate(x + 2.0*cm - 0.12*cm, y + 6.45*cm)
    c.rotate(90)
    c.drawRightString(0, 0, "Ausgang OR")
    c.restoreState()
    
    # Q3 label
    c.saveState()
    c.setFillColor(colors.HexColor('#7F8C8D'))
    c.setFont("Helvetica-Bold", 4.5)
    c.translate(x + 3.0*cm - 0.12*cm, y + 6.45*cm)
    c.rotate(90)
    c.drawRightString(0, 0, "Ausgang NOT")
    c.restoreState()

# --- DRAW CARD BASE LAYOUT ---

def draw_card_base(c, x, y, task):
    """Draws borders, ticks, badges, and side controls for the overlay card."""
    card_w = 9.0 * cm
    card_h = 7.0 * cm
    
    # Base card boundary (cut line)
    c.setStrokeColor(colors.HexColor('#BDC3C7'))
    c.setLineWidth(0.4)
    c.rect(x, y, card_w, card_h, stroke=True, fill=False)
    
    # --- CORNER TEXTS (Clean & small branding/ID in dedicated info boxes) ---
    draw_corner_boxes(c, x, y, task, card_w, card_h)
    
    # --- BOTTOM MARGIN: DIGITAL INPUTS (I1 to I8) ---
    for i in range(1, 9):
        px = x + i * cm
        
        # Line segment extending from bottom border to badge box
        c.setStrokeColor(colors.HexColor('#27AE60'))
        c.setLineWidth(0.8)
        c.line(px, y, px, y + 0.16*cm)
        
        # Badge rounded rectangle
        draw_badge(c, px, y + 0.3*cm, f"I{i}", badge_type="input")
        
    # --- TOP MARGIN: DIGITAL OUTPUTS (Q1 to Q8) ---
    for i in range(1, 9):
        px = x + i * cm
        py = y + card_h
        
        # Line segment extending from top border to badge box
        c.setStrokeColor(colors.HexColor('#2980B9'))
        c.setLineWidth(0.8)
        c.line(px, py, px, py - 0.16*cm)
        
        # Badge rounded rectangle
        draw_badge(c, px, py - 0.3*cm, f"Q{i}", badge_type="output")
        
    # --- LEFT MARGIN: SIDE LABELS & SWITCHES ---
    c.setStrokeColor(colors.HexColor('#95A5A6'))
    c.setLineWidth(0.6)
    left_ticks = [1.0, 2.0, 3.5, 4.5, 6.0]
    for ty_val in left_ticks:
        c.line(x, y + ty_val*cm, x + 0.12*cm, y + ty_val*cm)
        
    c.setFillColor(colors.HexColor('#7F8C8D'))
    c.setFont("Helvetica-Bold", 5.0)
    c.drawString(x + 0.15*cm, y + 1.0*cm - 1.5, "AI1")
    c.drawString(x + 0.15*cm, y + 3.5*cm - 1.5, "AI2")
    c.drawString(x + 0.15*cm, y + 6.0*cm - 1.5, "Enc")
    
    for ctrl in left_controls:
        cy_val = y + ctrl["y_rel"] * cm
        # Tick line
        c.setLineWidth(0.8)
        if ctrl["type"] == "analog":
            c.setStrokeColor(colors.HexColor('#E67E22'))
            fill_color = colors.HexColor('#FDF2E9')
            border_color = colors.HexColor('#F39C12')
            text_color = colors.HexColor('#935116')
        elif ctrl["type"] == "switch":
            c.setStrokeColor(colors.HexColor('#7F8C8D'))
            fill_color = colors.HexColor('#F2F4F4')
            border_color = colors.HexColor('#95A5A6')
            text_color = colors.HexColor('#2C3E50')
        else: # encoder
            c.setStrokeColor(colors.HexColor('#8E44AD'))
            fill_color = colors.HexColor('#F5EEF8')
            border_color = colors.HexColor('#9B59B6')
            text_color = colors.HexColor('#5B2C6F')
            
        c.line(x, cy_val, x + 0.17*cm, cy_val)
        
        # Badge
        c.setFillColor(fill_color)
        c.setStrokeColor(border_color)
        c.setLineWidth(0.5)
        c.roundRect(x + 0.17*cm, cy_val - lr_badge_h/2, lr_badge_w, lr_badge_h, 0.06*cm, fill=True, stroke=True)
        
        # Text
        c.setFillColor(text_color)
        c.setFont("Helvetica-Bold", 6.0)
        c.drawCentredString(x + 0.17*cm + lr_badge_w/2, cy_val - 2, ctrl["label"])
        
    # --- RIGHT MARGIN: SLIDER & SWITCH ---
    # Slider AI3 Track (2.0 to 6.0 cm)
    c.setStrokeColor(colors.HexColor('#BDC3C7'))
    c.setLineWidth(1.5)
    c.line(x + card_w - 0.2*cm, y + 2.0*cm, x + card_w - 0.2*cm, y + 6.0*cm)
    
    # Slider Knob representation at 3.5cm
    c.setFillColor(colors.HexColor('#7F8C8D'))
    c.setStrokeColor(colors.HexColor('#34495E'))
    c.setLineWidth(0.4)
    c.rect(x + card_w - 0.26*cm, y + 3.4*cm, 0.12*cm, 0.2*cm, fill=True, stroke=True)
    
    # Label AI3
    c.setFillColor(colors.HexColor('#7F8C8D'))
    c.setFont("Helvetica-Bold", 5.0)
    c.drawRightString(x + card_w - 0.35*cm, y + 3.5*cm - 1.5, "AI3")
    
    # Switch AI3/I3 at 6.5cm (toggled left)
    draw_switch_icon(c, x + card_w - 0.3*cm, y + 6.5*cm, position="left")
    c.drawRightString(x + card_w - 0.55*cm, y + 6.5*cm - 1.5, "AI3/I3")

def draw_card(c, x, y, task=None):
    """Draws a single logiBUS® Mini-Trainer card with border markings and task details."""
    card_w = 9.0 * cm
    card_h = 7.0 * cm
    
    c.setFillColor(colors.HexColor('#935116'))
    c.setFont("Helvetica-Bold", 6.0)
    c.drawCentredString(x + 8.8*cm - 0.17*cm - lr_badge_w/2, y + 3.5*cm - 2, "AI3")
    
    # Draw standard base card layout (borders, corner info boxes, badges, switch icons)
    draw_card_base(c, x, y, task)
    
    # Center coordinates of drawing area
    gc_x = x + 4.5 * cm
    gc_y = y + 3.5 * cm
    
    # Tick mark at 6.5cm
    c.setStrokeColor(colors.HexColor('#7F8C8D'))
    c.setLineWidth(0.8)
    c.line(x + 9.0*cm - 0.17*cm, cy_val, x + 9.0*cm, cy_val)
    
    # Vertical indicator line from badge to tick
    c.line(x + 9.0*cm - 0.17*cm, badge_y, x + 9.0*cm - 0.17*cm, cy_val)
    
    # Switch Badge
    c.setFillColor(colors.HexColor('#F2F4F4'))
    c.setStrokeColor(colors.HexColor('#95A5A6'))
    c.setLineWidth(0.5)
    c.roundRect(x + 9.0*cm - 0.17*cm - lr_badge_w, badge_y - lr_badge_h/2, lr_badge_w, lr_badge_h, 0.06*cm, fill=True, stroke=True)
    
    c.setFillColor(colors.HexColor('#2C3E50'))
    c.setFont("Helvetica-Bold", 6.0)
    c.drawCentredString(x + 9.0*cm - 0.17*cm - lr_badge_w/2, badge_y - 2, "AI3/I3")
    
    # --- TASK / EXERCISE CENTRAL AREA ---
    # Task bounds: x + 1.7*cm to x + 7.3*cm, y + 0.7*cm to y + 6.3*cm
    tx_start = x + 1.7 * cm
    ty_start = y + 0.7 * cm
    t_w = 5.6 * cm
    t_h = 5.6 * cm
    
    # Draw inner task border
    c.setStrokeColor(colors.HexColor('#BDC3C7'))
    c.setLineWidth(0.5)
    c.rect(tx_start, ty_start, t_w, t_h, stroke=True, fill=False)
    
    # Dotted grid background
    draw_dotted_grid(c, tx_start, ty_start, t_w, t_h, step=0.4*cm)
    
    # Header bar
    hb_h = 0.65 * cm
    c.setFillColor(colors.HexColor('#2C3E50'))
    c.rect(tx_start, ty_start + t_h - hb_h, t_w, hb_h, fill=True, stroke=False)
    
    # Header text
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 5.5)
    c.drawString(tx_start + 0.15*cm, ty_start + t_h - 0.2*cm, "logiBUS\u00ae Mini-Trainer")
    c.setFont("Helvetica-Bold", 4.2)
    c.drawRightString(tx_start + t_w - 0.15*cm, ty_start + t_h - 0.2*cm, "Powered by 4diac\u2122")
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(tx_start + 0.15*cm, ty_start + t_h - 0.5*cm, "\u00dcBUNG 1: SELBSTHALTUNG")
    
    # Draw Ladder Diagram (LD) Schematic
    # Left Rail
    c.setStrokeColor(colors.HexColor('#2C3E50'))
    c.setLineWidth(1.0)
    c.line(tx_start + 0.5*cm, ty_start + 1.5*cm, tx_start + 0.5*cm, ty_start + 4.2*cm)
    # Right Rail
    c.line(tx_start + t_w - 0.5*cm, ty_start + 1.5*cm, tx_start + t_w - 0.5*cm, ty_start + 4.2*cm)
    
    # Rung 1 at y = ty_start + 3.5cm
    ry = ty_start + 3.5 * cm
    c.line(tx_start + 0.5*cm, ry, tx_start + 1.0*cm, ry)
    draw_contact(c, tx_start + 1.4*cm, ry, "I1 (Start)")
    c.line(tx_start + 1.8*cm, ry, tx_start + 2.4*cm, ry)
    draw_contact(c, tx_start + 2.8*cm, ry, "I2 (Stop)", nc=True)
    c.line(tx_start + 3.2*cm, ry, tx_start + 4.2*cm, ry)
    draw_coil(c, tx_start + 4.6*cm, ry, "Q1")
    c.line(tx_start + 5.0*cm, ry, tx_start + t_w - 0.5*cm, ry)
    
    # Rung 1 Parallel Branch (Self-holding contact Q1) at y = ty_start + 2.5cm
    ry_branch = ty_start + 2.5 * cm
    # Vertical drop lines
    c.line(tx_start + 0.8*cm, ry, tx_start + 0.8*cm, ry_branch)
    c.line(tx_start + 2.0*cm, ry, tx_start + 2.0*cm, ry_branch)
    # Horizontal branch with contact
    c.line(tx_start + 0.8*cm, ry_branch, tx_start + 1.0*cm, ry_branch)
    draw_contact(c, tx_start + 1.4*cm, ry_branch, "Q1")
    c.line(tx_start + 1.8*cm, ry_branch, tx_start + 2.0*cm, ry_branch)
    
    # Text Description Box
    c.setFillColor(colors.HexColor('#F8F9F9'))
    c.setStrokeColor(colors.HexColor('#BDC3C7'))
    c.setLineWidth(0.4)
    desc_y = ty_start + 0.8 * cm
    desc_h = 0.55 * cm
    c.roundRect(tx_start + 0.15*cm, desc_y, t_w - 0.3*cm, desc_h, 0.05*cm, fill=True, stroke=True)
    
    c.setFillColor(colors.HexColor('#34495E'))
    c.setFont("Helvetica", 5)
    c.drawString(tx_start + 0.25*cm, desc_y + 0.38*cm, "Beschreibung: Tastendruck auf I1 schaltet Ausgang Q1 ein.")
    c.drawString(tx_start + 0.25*cm, desc_y + 0.24*cm, "Q1 haelt sich selbst ueber den Hilfskontakt Q1.")
    c.drawString(tx_start + 0.25*cm, desc_y + 0.1*cm, "Oeffner I2 unterbricht den Selbsthaltekreis und schaltet Q1 aus.")
    
    # Metadata Footer
    meta_y = ty_start + 0.15 * cm
    c.setFillColor(colors.HexColor('#7F8C8D'))
    c.setFont("Helvetica-Oblique", 4.5)
    c.drawString(tx_start + 0.2*cm, meta_y + 0.25*cm, "Name: _______________________")
    c.drawString(tx_start + 0.2*cm, meta_y, "Datum: ______________________")
    c.drawRightString(tx_start + t_w - 0.2*cm, meta_y + 0.25*cm, "Klasse: _________")
    c.drawRightString(tx_start + t_w - 0.2*cm, meta_y, "Bewertung: ______")

# --- PDF GENERATOR FUNCTIONS ---

def generate_single_card_pdf(filename="logiBUS_single_card.pdf", tasks=None):
    """Generates a PDF containing centered cards for all tasks, one card per page."""
    if tasks is None:
        tasks = load_tasks()
        
    c = canvas.Canvas(filename, pagesize=A4)
    
    page_w, page_h = A4
    card_w = 9.0 * cm
    card_h = 7.0 * cm
    
    x = (page_w - card_w) / 2.0
    y = (page_h - card_h) / 2.0
    
    for task in tasks:
        # Draw Page Title and Help Info (outside crop marks)
        c.setFillColor(colors.HexColor('#2C3E50'))
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(page_w/2, page_h - 2*cm, "logiBUS\u00ae Mini-Trainer - Einzelschablone")
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor('#7F8C8D'))
        c.drawCentredString(page_w/2, page_h - 2.5*cm, "Druckeinstellungen: 100% Gr\u00f6\u00dfe (Tats\u00e4chliche Gr\u00f6\u00dfe), Hochformat")
        c.drawCentredString(page_w/2, page_h - 2.9*cm, f"Kartengr\u00f6\u00dfe: {card_w/cm:.1f} cm x {card_h/cm:.1f} cm. Bitte an den Schnittmarken ausschneiden.")
        
        # Draw card
        draw_card(c, x, y, task)
        
        # Draw crop marks
        draw_crop_marks(c, x, y, card_w, card_h)
        
        # Draw task description (outside the card area, at the bottom of the page)
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.HexColor('#2C3E50'))
        c.drawCentredString(page_w/2, 4*cm, "AUFGABENBESCHREIBUNG:")
        
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor('#34495E'))
        desc = task.get("description", "")
        
        # Simple line wrapping
        words = desc.split(' ')
        lines = []
        curr = ""
        for w in words:
            test = curr + " " + w if curr else w
            if c.stringWidth(test, "Helvetica", 9) < (page_w - 4*cm):
                curr = test
            else:
                lines.append(curr)
                curr = w
        if curr:
            lines.append(curr)
            
        for idx, l in enumerate(lines[:5]):
            c.drawCentredString(page_w/2, 3.4*cm - idx*14, l)
            
        c.showPage()
        
    try:
        c.save()
        print(f"Successfully generated {filename}")
    except OSError as e:
        print(f"Error: Could not save single card PDF to '{filename}'. Reason: {e}")
        print("Please check if the file is currently open in another program (e.g. Acrobat Reader) or if you lack write permissions.")

def generate_multi_cards_pdf(filename="logiBUS_multi_cards.pdf", tasks=None):
    """Generates a PDF containing a paper-saving grid of cards (2 columns x 4 rows) for all tasks."""
    if tasks is None:
        tasks = load_tasks()
        
    c = canvas.Canvas(filename, pagesize=A4)
    
    page_w, page_h = A4
    card_w = 9.0 * cm
    card_h = 7.0 * cm
    
    cols = 2
    rows = 4
    cards_per_page = cols * rows
    
    # Center grid on A4
    grid_w = cols * card_w
    grid_h = rows * card_h
    
    start_x = (page_w - grid_w) / 2.0
    start_y = (page_h - grid_h) / 2.0
    
    num_pages = (len(tasks) + cards_per_page - 1) // cards_per_page
    
    for page_idx in range(num_pages):
        draw_crop_marks(c, start_x, start_y, grid_w, grid_h, length=0.8*cm, offset=0.2*cm)
        
        for slot in range(cards_per_page):
            task_idx = page_idx * cards_per_page + slot
            if task_idx >= len(tasks):
                break
                
            task = tasks[task_idx]
            col = slot % cols
            row = slot // cols
            
            grid_row = (rows - 1) - row
            x = start_x + col * card_w
            y = start_y + grid_row * card_h
            
            draw_card(c, x, y, task)
            
        c.showPage()
        
    try:
        c.save()
        print(f"Successfully generated {filename}")
    except OSError as e:
        print(f"Error: Could not save multi card PDF to '{filename}'. Reason: {e}")
        print("Please check if the file is currently open in another program (e.g. Acrobat Reader) or if you lack write permissions.")

if __name__ == "__main__":
    tasks_list = load_tasks()
    generate_single_card_pdf(tasks=tasks_list)
    generate_multi_cards_pdf(tasks=tasks_list)
