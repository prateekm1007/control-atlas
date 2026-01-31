from fpdf import FPDF
import numpy as np

def generate_v14_certificate(sig, verdict, score, gen, rationale, results, atoms):
    pdf = FPDF(); pdf.set_auto_page_break(True); pdf.add_page()
    pdf.set_font("helvetica", "B", 18); pdf.cell(0, 15, "TOSCANINI FORENSIC NOTARY CERTIFICATE", ln=True, align='C')
    
    # DECISION BLOCK
    color = (180, 0, 0) if verdict == "VETO" else (0, 100, 0)
    pdf.set_fill_color(245, 245, 245); pdf.set_text_color(*color); pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 12, f"DECISION: {verdict} / PHYSICAL INTEGRITY: {score}%", ln=True, align='C', fill=True)
    pdf.set_text_color(0); pdf.ln(5)

    # EXECUTIVE NARRATIVE
    pdf.set_font("helvetica", "B", 11); pdf.cell(0, 8, "EXECUTIVE BIOPHYSICAL SYNTHESIS", ln=True)
    pdf.set_font("helvetica", "", 10); pdf.multi_cell(0, 5, str(rationale).encode('ascii', 'ignore').decode())

    # METRIC INTERPRETATION (The Pharma Section)
    pdf.ln(5); pdf.set_fill_color(230, 240, 250); pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 8, "TECHNICAL METRIC INTERPRETATION", ln=True, fill=True)
    pdf.set_font("helvetica", "", 9)
    interp = "Physical Score: Confirms adherence to invariant laws of atomic exclusion. " \
             "ML Confidence (pLDDT): Represents the predicted C-alpha local distance difference test. " \
             "Scores < 70 indicate regions where tertiary side-chain packing is speculative and docking is high-risk."
    pdf.multi_cell(0, 4, interp)

    # Figures
    ca = [a.pos for a in atoms if (a.atom_name if hasattr(a, 'atom_name') else a.get('atom')) == 'CA']
    if len(ca) > 4:
        pdf.ln(5); coords = np.array(ca); xs, ys = coords[:, 0], coords[:, 1]
        mx, my, span = np.min(xs), np.min(ys), max(1, np.max(xs)-np.min(xs))
        scale, bx, by = 60/span, 30, pdf.get_y()+10
        pdf.set_draw_color(150, 150, 150); pdf.set_line_width(0.8)
        for i in range(len(ca)-1): pdf.line(bx+(ca[i][0]-mx)*scale, by+(ca[i][1]-my)*scale, bx+(ca[i+1][0]-mx)*scale, by+(ca[i+1][1]-my)*scale)
        bx2 = 120; pdf.set_draw_color(100, 120, 140)
        for i in range(len(ca)-1): pdf.line(bx2+(ca[i][2]-mx)*scale, by+(ca[i][1]-my)*scale, bx2+(ca[i+1][2]-mx)*scale, by+(ca[i+1][1]-my)*scale)

    pdf.add_page(); pdf.set_font("helvetica", "B", 16); pdf.cell(0, 15, "TECHNICAL ANNEX (10-LAW CANON)", ln=True)
    for l in results:
        pdf.set_font("helvetica", "B", 9); pdf.cell(0, 6, f"{l['law_id']}: {l['title']} [{l['status']}]", ln=True)
        pdf.set_font("helvetica", "", 8); pdf.multi_cell(0, 4, f"Observed: {l['measurement']}\nPrinciple: {l['principle']}"); pdf.ln(2)
    return pdf.output()
