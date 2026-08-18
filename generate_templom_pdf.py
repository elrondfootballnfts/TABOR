import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable

def create_templom_pdf():
    pdf_path = "TEMPLOM_Nyomtathato_Kellekek.pdf"
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=30,
        rightMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0f172a'),
        alignment=1,
        spaceAfter=10
    )
    card_title = ParagraphStyle(
        'CardTitle',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1e3a8a'),
        alignment=0,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#334155')
    )
    box_inst = ParagraphStyle(
        'BoxInst',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#0369a1'),
        fontName='Helvetica-Oblique'
    )
    corner_word_style = ParagraphStyle(
        'CornerWord',
        parent=styles['Normal'],
        fontSize=12,
        leading=14,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#ffffff'),
        alignment=1
    )

    elements = []

    # Title
    elements.append(Paragraph("🏛️ TEMPLOM JÁTÉK - NYOMTATHATÓ TEREPI KELLÉKEK", title_style))
    elements.append(Paragraph("<b>Használati útmutató:</b> Nyomtasd ki ezt a dokumentumot! Vágd ki a 4 állomás kártyáit a szaggatott vonalak mentén, és helyezd el őket a megadott tábori helyszíneken.", body_style))
    elements.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # 1. ÁLLOMÁS: CARDAN-RÁCS ÉS FEDŐSABLON
    # -------------------------------------------------------------
    elements.append(Paragraph("<b>1. ÁLLOMÁS (Lépcső alja) – CARDAN-RÁCS & ABLAKOS SABLON</b>", card_title))
    elements.append(Paragraph("<i>Instrukció a szervezőnek:</i> Vágd ki az <b>1/A Alapkártyát</b> és az <b>1/B Fedősablont</b>. Az 1/B sablonon vágd ki sniccerrel/ollóval a 6 db szürke [LYUK] ablakot! Tedd a kettőt egy tasakba a lépcsőnél.", box_inst))
    elements.append(Spacer(1, 6))

    # Table 1/A: Base grid with hidden ALAPKŐ
    # Grid 5x5:
    # Row 1: [A]  R   T   Z   M
    # Row 2:  B  [L]  K   D   P
    # Row 3:  S   N  [A]  V   G
    # Row 4:  E   F   H  [P]  J
    # Row 5: [K]  U   W   Y  [Ő]
    grid1_data = [
        ['A', 'R', 'T', 'Z', 'M'],
        ['B', 'L', 'K', 'D', 'P'],
        ['S', 'N', 'A', 'V', 'G'],
        ['E', 'F', 'H', 'P', 'J'],
        ['K', 'U', 'W', 'Y', 'Ő']
    ]
    t1_grid = Table(grid1_data, colWidths=[24]*5, rowHeights=[20]*5)
    t1_grid.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#64748b')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 11),
    ]))

    # Table 1/B: Mask overlay (holes at (0,0), (1,1), (2,2), (3,3), (0,4), (4,4))
    grid1_mask = [
        ['[LYUK]', '███', '███', '███', '███'],
        ['███', '[LYUK]', '███', '███', '███'],
        ['███', '███', '[LYUK]', '███', '███'],
        ['███', '███', '███', '[LYUK]', '███'],
        ['[LYUK]', '███', '███', '███', '[LYUK]']
    ]
    t1_mask = Table(grid1_mask, colWidths=[24]*5, rowHeights=[20]*5)
    t1_mask.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#000000')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#ffffff')),
        ('BACKGROUND', (1,1), (1,1), colors.HexColor('#ffffff')),
        ('BACKGROUND', (2,2), (2,2), colors.HexColor('#ffffff')),
        ('BACKGROUND', (3,3), (3,3), colors.HexColor('#ffffff')),
        ('BACKGROUND', (0,4), (0,4), colors.HexColor('#ffffff')),
        ('BACKGROUND', (4,4), (4,4), colors.HexColor('#ffffff')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 7),
    ]))

    badge_el = Table([[Paragraph("TITKOS SZÓ:<br/><b>ÉL</b>", corner_word_style)]], colWidths=[80], rowHeights=[32])
    badge_el.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0284c7')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('CORNER_RADIUS', (0,0), (-1,-1), 6)
    ]))

    card1_cell_left = [
        Paragraph("<b>1/A: ALAPKŐ BETŰRÁCS</b>", ParagraphStyle('H4', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold')),
        Spacer(1, 4),
        t1_grid,
        Spacer(1, 4),
        Paragraph("<i>Alapkarton a tasakban</i>", box_inst)
    ]
    card1_cell_right = [
        Paragraph("<b>1/B: FEDŐSABLON (Vágd ki a fehér lyukakat!)</b>", ParagraphStyle('H4', parent=styles['Normal'], fontSize=8.5, fontName='Helvetica-Bold')),
        Spacer(1, 4),
        t1_mask,
        Spacer(1, 4),
        badge_el
    ]

    card1_table = Table([[card1_cell_left, card1_cell_right]], colWidths=[240, 280])
    card1_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#0284c7')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0f9ff')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    elements.append(card1_table)
    elements.append(Spacer(1, 14))

    # -------------------------------------------------------------
    # 2. ÁLLOMÁS: DÖRZSÖLŐS FASZÉN LAP
    # -------------------------------------------------------------
    elements.append(Paragraph("<b>2. ÁLLOMÁS (Tábortűz) – FASZÉN-DÖRZSÖLŐS TITKOS LAP</b>", card_title))
    elements.append(Paragraph("<i>Instrukció a szervezőnek:</i> Írd rá egy sima lapra keményen, rányomott golyóstollal az <b>ÁLDOZAT</b> szót a középső fehér keretbe, hogy a barázdák meglegyenek. A gyerekek faszénnel dörzsölik át!", box_inst))
    elements.append(Spacer(1, 6))

    badge_ok = Table([[Paragraph("TITKOS SZÓ:<br/><b>ŐK</b>", corner_word_style)]], colWidths=[80], rowHeights=[32])
    badge_ok.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ea580c')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))

    card2_content = [
        Paragraph("<b>🪵 2. ÁLLOMÁS - AZ OLTÁR HAMVA</b>", ParagraphStyle('H4', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold', textColor=colors.HexColor('#9a3412'))),
        Spacer(1, 4),
        Paragraph("<i>„Végy egy darabka faszenet a tábortűzből (vagy egy ceruzát), és finoman dörzsöld át ezt a fehér mezőt, hogy a hamuból feltáruljon a titok!”</i>", body_style),
        Spacer(1, 10),
        Table([["\n\n\n[ ITT DÖRZSÖLD ÁT A FASZÉNNEL ]\n\n\n"]], colWidths=[380], rowHeights=[60], style=[
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#94a3b8')),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ffffff')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Oblique'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#94a3b8'))
        ]),
        Spacer(1, 8),
        badge_ok
    ]

    card2_table = Table([[card2_content]], colWidths=[520])
    card2_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#ea580c')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fff7ed')),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    elements.append(card2_table)

    elements.append(PageBreak())

    # -------------------------------------------------------------
    # 3. ÁLLOMÁS: CÉZÁR-KÓD MENÓRA
    # -------------------------------------------------------------
    elements.append(Paragraph("<b>3. ÁLLOMÁS (Lámpaoszlop) – CÉZÁR-TITKOSÍRÁS</b>", card_title))
    elements.append(Paragraph("<i>Instrukció a szervezőnek:</i> Ragaszd fel a kerti lámpaoszlop vagy lámpás oldalára.", box_inst))
    elements.append(Spacer(1, 6))

    badge_ov = Table([[Paragraph("TITKOS SZÓ:<br/><b>ÖV</b>", corner_word_style)]], colWidths=[80], rowHeights=[32])
    badge_ov.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ca8a04')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))

    card3_content = [
        Paragraph("<b>🕎 3. ÁLLOMÁS - A MENÓRA VILÁGOSSÁGA</b>", ParagraphStyle('H4', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold', textColor=colors.HexColor('#854d0e'))),
        Spacer(1, 4),
        Paragraph("KÓDOLT SZÖVEG:", ParagraphStyle('Sub', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold')),
        Spacer(1, 2),
        Table([["W - J - M - B - H - P - T - T - B - H"]], colWidths=[380], rowHeights=[28], style=[
            ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#ca8a04')),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fef9c3')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 12),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#713f12'))
        ]),
        Spacer(1, 6),
        Paragraph("🗝️ <i>„A világosság visszavezet a fényre! Lépj MINDEN betűvel EGGYEL VISSZA az ábécében!” (Pl. B ➔ A, K ➔ J, W ➔ V)</i>", body_style),
        Spacer(1, 8),
        badge_ov
    ]

    card3_table = Table([[card3_content]], colWidths=[520])
    card3_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#ca8a04')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fefce8')),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    elements.append(card3_table)
    elements.append(Spacer(1, 14))

    # -------------------------------------------------------------
    # 4. ÁLLOMÁS: ÁTVILÁGÍTÓS KÁRPIT
    # -------------------------------------------------------------
    elements.append(Paragraph("<b>4. ÁLLOMÁS (Nagyterem legbelső ajtaja) – ÁTVILÁGÍTÓS KÁRPIT</b>", card_title))
    elements.append(Paragraph("<i>Instrukció a szervezőnek:</i> Ennek a lapnak a <b>hátoldalára</b> vastag fekete filccel írd fel a mellékelt sablon szerint: <b>SZENTEK SZENTJE</b>. Amikor a napfény/vaku felé tartják, átvilágít!", box_inst))
    elements.append(Spacer(1, 6))

    badge_ek = Table([[Paragraph("TITKOS SZÓ:<br/><b>EK</b>", corner_word_style)]], colWidths=[80], rowHeights=[32])
    badge_ek.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#7c3aed')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))

    card4_content = [
        Paragraph("<b>🚪 4. ÁLLOMÁS - A KETTÉHASADT KÁRPIT</b>", ParagraphStyle('H4', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold', textColor=colors.HexColor('#581c87'))),
        Spacer(1, 4),
        Paragraph("<i>„A kárpit felülről az aljáig kettéhasadt! Tartsd ezt a lapot a NAPFÉNY vagy a MOBILOD VAKUJA felé, és olvasd össze az átvilágító szavakat!”</i>", body_style),
        Spacer(1, 10),
        Table([["░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░\n░░░░░░░░░░░ [ TARTSD A FÉNY FELÉ! ] ░░░░░░░░░░░\n░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░"]], colWidths=[380], rowHeights=[50], style=[
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#7c3aed')),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#faf5ff')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#6b21a8'))
        ]),
        Spacer(1, 8),
        badge_ek
    ]

    card4_table = Table([[card4_content]], colWidths=[520])
    card4_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#7c3aed')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#faf5ff')),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    elements.append(card4_table)

    doc.build(elements)
    print(f"Sikeresen legenerálva: {pdf_path}")

if __name__ == "__main__":
    create_templom_pdf()
