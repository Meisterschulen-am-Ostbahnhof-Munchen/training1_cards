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

def draw_contact(c, cx, cy, label, nc=False):
    """Draws a ladder logic contact (NO or NC)."""
    c.setStrokeColor(colors.HexColor('#2C3E50'))
    c.setLineWidth(0.8)
    
    # Left and right lead lines
    c.line(cx - 3.5*mm, cy, cx - 1.2*mm, cy)
    c.line(cx + 1.2*mm, cy, cx + 3.5*mm, cy)
    
    # Parallel contact plates
    c.line(cx - 1.2*mm, cy - 2.5*mm, cx - 1.2*mm, cy + 2.5*mm)
    c.line(cx + 1.2*mm, cy - 2.5*mm, cx + 1.2*mm, cy + 2.5*mm)
    
    if nc:
        # Diagonal line for NC
        c.line(cx - 2.2*mm, cy - 3.0*mm, cx + 2.2*mm, cy + 3.0*mm)
        
    # Contact label
    c.setFillColor(colors.HexColor('#2C3E50'))
    c.setFont("Helvetica-Bold", 6.5)
    c.drawCentredString(cx, cy + 3.2*mm, label)

def draw_coil(c, cx, cy, label):
    """Draws a ladder logic coil."""
    c.setStrokeColor(colors.HexColor('#2C3E50'))
    c.setLineWidth(0.8)
    
    # Lead lines
    c.line(cx - 5.0*mm, cy, cx - 2.5*mm, cy)
    c.line(cx + 2.5*mm, cy, cx + 5.0*mm, cy)
    
    # Coil brackets/parentheses representation (or circle)
    c.setFillColor(colors.white)
    c.circle(cx, cy, 2.5*mm, fill=True, stroke=True)
    
    # Coil label
    c.setFillColor(colors.HexColor('#2C3E50'))
    c.setFont("Helvetica-Bold", 6.5)
    c.drawCentredString(cx, cy + 3.2*mm, label)

def draw_dotted_grid(c, x, y, w, h, step=0.4*cm):
    """Draws a subtle dotted background grid for the exercise area."""
    c.setFillColor(colors.HexColor('#BDC3C7'))
    
    nx = int(w / step) + 1
    ny = int(h / step) + 1
    
    for i in range(1, nx - 1):
        for j in range(1, ny - 1):
            px = x + i * step
            py = y + j * step
            c.circle(px, py, 0.4*mm, fill=True, stroke=False)

def draw_card(c, x, y):
    """Draws a single logiBUS® Mini-Trainer card with border markings and a sample task."""
    card_w = 9.0 * cm
    card_h = 7.0 * cm
    
    # Draw base card boundary (cut line)
    c.setStrokeColor(colors.HexColor('#BDC3C7'))
    c.setLineWidth(0.4)
    c.rect(x, y, card_w, card_h, stroke=True, fill=False)
    
    # Badge sizes
    tb_badge_w = 0.55 * cm
    tb_badge_h = 0.3 * cm
    
    lr_badge_w = 1.1 * cm
    lr_badge_h = 0.3 * cm
    
    # --- BOTTOM MARGIN: DIGITAL INPUTS (I1 to I8) ---
    for i in range(1, 9):
        px = x + i * cm
        # Tick line pointing inward
        c.setStrokeColor(colors.HexColor('#27AE60'))
        c.setLineWidth(0.8)
        c.line(px, y, px, y + 0.15*cm)
        
        # Badge
        c.setFillColor(colors.HexColor('#E8F8F5'))
        c.setStrokeColor(colors.HexColor('#2ECC71'))
        c.setLineWidth(0.5)
        c.roundRect(px - tb_badge_w/2, y + 0.15*cm, tb_badge_w, tb_badge_h, 0.06*cm, fill=True, stroke=True)
        
        # Label
        c.setFillColor(colors.HexColor('#1E8449'))
        c.setFont("Helvetica-Bold", 6.5)
        c.drawCentredString(px, y + 0.23*cm, f"I{i}")
        
    # --- TOP MARGIN: DIGITAL OUTPUTS (Q1 to Q8) ---
    for i in range(1, 9):
        px = x + i * cm
        py = y + card_h
        # Tick line pointing inward
        c.setStrokeColor(colors.HexColor('#2980B9'))
        c.setLineWidth(0.8)
        c.line(px, py, px, py - 0.15*cm)
        
        # Badge
        c.setFillColor(colors.HexColor('#EBF5FB'))
        c.setStrokeColor(colors.HexColor('#3498DB'))
        c.setLineWidth(0.5)
        c.roundRect(px - tb_badge_w/2, py - 0.45*cm, tb_badge_w, tb_badge_h, 0.06*cm, fill=True, stroke=True)
        
        # Label
        c.setFillColor(colors.HexColor('#1B4F72'))
        c.setFont("Helvetica-Bold", 6.5)
        c.drawCentredString(px, py - 0.37*cm, f"Q{i}")
        
    # --- LEFT MARGIN: ANALOG INPUTS & SWITCHES ---
    left_controls = [
        {"y_rel": 1.0, "label": "AI1", "type": "analog"},
        {"y_rel": 2.0, "label": "AI1/I1", "type": "switch"},
        {"y_rel": 3.5, "label": "AI2", "type": "analog"},
        {"y_rel": 4.5, "label": "AI2/I2", "type": "switch"},
        {"y_rel": 6.0, "label": "Enc", "type": "encoder"}
    ]
    
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
        c.drawCentredString(x + 0.17*cm + lr_badge_w/2, cy_val - 0.7*mm, ctrl["label"])
        
    # --- RIGHT MARGIN: SLIDER & SWITCH ---
    # Slider AI3 Track (2.0 to 6.0 cm)
    c.setStrokeColor(colors.HexColor('#BDC3C7'))
    c.setLineWidth(2.2)
    c.line(x + 8.8*cm, y + 2.0*cm, x + 8.8*cm, y + 6.0*cm)
    
    # Slider Knob representation at 3.5cm
    c.setFillColor(colors.HexColor('#7F8C8D'))
    c.setStrokeColor(colors.HexColor('#34495E'))
    c.setLineWidth(0.5)
    c.rect(x + 8.71*cm, y + 3.35*cm, 0.18*cm, 0.3*cm, fill=True, stroke=True)
    
    # Tick mark for Slider center (AI3) at 3.5cm
    c.setStrokeColor(colors.HexColor('#E67E22'))
    c.setLineWidth(0.8)
    c.line(x + 9.0*cm, y + 3.5*cm, x + 8.65*cm, y + 3.5*cm)
    
    # Slider Badge
    c.setFillColor(colors.HexColor('#FDF2E9'))
    c.setStrokeColor(colors.HexColor('#F39C12'))
    c.setLineWidth(0.5)
    c.roundRect(x + 8.8*cm - 0.17*cm - lr_badge_w, y + 3.5*cm - lr_badge_h/2, lr_badge_w, lr_badge_h, 0.06*cm, fill=True, stroke=True)
    
    c.setFillColor(colors.HexColor('#935116'))
    c.setFont("Helvetica-Bold", 6.0)
    c.drawCentredString(x + 8.8*cm - 0.17*cm - lr_badge_w/2, y + 3.5*cm - 0.7*mm, "AI3")
    
    # Switch AI3 vs I3 at 6.5cm
    cy_val = y + 6.5*cm
    
    # To prevent overlap with Q8, we shift the badge down to y + 5.9*cm and draw a neat routing line
    badge_y = y + 5.9*cm
    
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
    c.drawCentredString(x + 9.0*cm - 0.17*cm - lr_badge_w/2, badge_y - 0.7*mm, "AI3/I3")
    
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

def generate_single_card_pdf(filename="logiBUS_single_card.pdf"):
    """Generates a PDF containing exactly one card centered on an A4 sheet with crop marks."""
    c = canvas.Canvas(filename, pagesize=A4)
    
    page_w, page_h = A4
    card_w = 9.0 * cm
    card_h = 7.0 * cm
    
    # Compute center coordinates
    x = (page_w - card_w) / 2.0
    y = (page_h - card_h) / 2.0
    
    # Draw Page Title and Help Info (outside crop marks)
    c.setFillColor(colors.HexColor('#2C3E50'))
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(page_w/2, page_h - 2*cm, "logiBUS\u00ae Mini-Trainer - Einzelschablone")
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor('#7F8C8D'))
    c.drawCentredString(page_w/2, page_h - 2.5*cm, "Druckeinstellungen: 100% Gr\u00f6\u00dfe (Tats\u00e4chliche Gr\u00f6\u00dfe), Hochformat")
    c.drawCentredString(page_w/2, page_h - 2.9*cm, f"Kartengr\u00f6\u00dfe: {card_w/cm:.1f} cm x {card_h/cm:.1f} cm. Bitte an den Schnittmarken ausschneiden.")
    
    # Draw card
    draw_card(c, x, y)
    
    # Draw crop marks
    draw_crop_marks(c, x, y, card_w, card_h)
    
    c.showPage()
    try:
        c.save()
        print(f"Successfully generated {filename}")
    except OSError as e:
        print(f"Error: Could not save single card PDF to '{filename}'. Reason: {e}")
        print("Please check if the file is currently open in another program (e.g. Acrobat Reader) or if you lack write permissions.")

def generate_multi_cards_pdf(filename="logiBUS_multi_cards.pdf"):
    """Generates a PDF containing a paper-saving grid of 8 cards (2 columns x 4 rows)."""
    c = canvas.Canvas(filename, pagesize=A4)
    
    page_w, page_h = A4
    card_w = 9.0 * cm
    card_h = 7.0 * cm
    
    cols = 2
    rows = 4
    
    # Calculate starting offsets to perfectly center the grid on A4
    grid_w = cols * card_w
    grid_h = rows * card_h
    
    start_x = (page_w - grid_w) / 2.0
    start_y = (page_h - grid_h) / 2.0
    
    # Draw background cutting helpers and crop marks around the outer edge of the grid
    draw_crop_marks(c, start_x, start_y, grid_w, grid_h, length=0.8*cm, offset=0.2*cm)
    
    # Draw each card in the grid
    for row in range(rows):
        for col in range(cols):
            x = start_x + col * card_w
            y = start_y + row * card_h
            draw_card(c, x, y)
            
    c.showPage()
    try:
        c.save()
        print(f"Successfully generated {filename}")
    except OSError as e:
        print(f"Error: Could not save multi card PDF to '{filename}'. Reason: {e}")
        print("Please check if the file is currently open in another program (e.g. Acrobat Reader) or if you lack write permissions.")

if __name__ == "__main__":
    generate_single_card_pdf()
    generate_multi_cards_pdf()
