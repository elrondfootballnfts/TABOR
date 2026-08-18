import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def register_unicode_fonts():
    font_paths = {
        'Arial': 'C:/Windows/Fonts/arial.ttf',
        'Arial-Bold': 'C:/Windows/Fonts/arialbd.ttf',
        'Arial-Italic': 'C:/Windows/Fonts/ariali.ttf'
    }
    for font_name, path in font_paths.items():
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, path))
            except Exception:
                pass

def create_templom_pdf():
    register_unicode_fonts()
    pdf_path = "TEMPLOM_Nyomtatando_Kartyak.pdf"
    
    # A4: 595 x 842 pt. Margins: 24 pt -> Available width: 547 pt, Height: 794 pt
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=24,
        rightMargin=24,
        topMargin=24,
        bottomMargin=24
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'MainTitle',
        fontName='Arial-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#0f172a'),
        alignment=1,
        spaceAfter=2
    )
    sub_title_style = ParagraphStyle(
        'SubTitle',
        fontName='Arial',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceAfter=8
    )

    card_header_1 = ParagraphStyle('CH1', fontName='Arial-Bold', fontSize=12, leading=15, textColor=colors.HexColor('#0284c7'))
    card_header_2 = ParagraphStyle('CH2', fontName='Arial-Bold', fontSize=12, leading=15, textColor=colors.HexColor('#ea580c'))
    card_header_3 = ParagraphStyle('CH3', fontName='Arial-Bold', fontSize=12, leading=15, textColor=colors.HexColor('#ca8a04'))
    card_header_4 = ParagraphStyle('CH4', fontName='Arial-Bold', fontSize=12, leading=15, textColor=colors.HexColor('#7c3aed'))

    body_style = ParagraphStyle('BodyDark', fontName='Arial', fontSize=9.5, leading=13.5, textColor=colors.HexColor('#1e293b'))
    box_inst = ParagraphStyle('BoxInst', fontName='Arial-Italic', fontSize=8, leading=10.5, textColor=colors.HexColor('#64748b'))
    
    badge_style = ParagraphStyle(
        'BadgeText',
        fontName='Arial-Bold',
        fontSize=11,
        leading=13,
        textColor=colors.HexColor('#ffffff'),
        alignment=1
    )

    elements = []

    # =========================================================================
    # PAGE 1: 1. ÁLLOMÁS & 2. ÁLLOMÁS
    # =========================================================================
    elements.append(Paragraph("TEMPLOM KINCSKERESŐ JÁTÉK - NYOMTATANDÓ KELLÉKEK", title_style))
    elements.append(Paragraph("Vágd ki a kártyákat a külső színes keretek mentén, és helyezd el őket a megadott tábori helyszíneken!", sub_title_style))

    # --- 1. ÁLLOMÁS ---
    grid1_data = [
        ['A', 'R', 'T', 'Z', 'M'],
        ['B', 'L', 'K', 'D', 'P'],
        ['S', 'N', 'A', 'V', 'G'],
        ['E', 'F', 'H', 'P', 'J'],
        ['K', 'U', 'W', 'Y', 'Ő']
    ]
    t1_grid = Table(grid1_data, colWidths=[27]*5, rowHeights=[24]*5)
    t1_grid.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#475569')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ffffff')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,-1), 'Arial-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 13),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#0f172a')),
    ]))

    grid1_mask = [
        ['[LYUK]', 'X X X', 'X X X', 'X X X', 'X X X'],
        ['X X X', '[LYUK]', 'X X X', 'X X X', 'X X X'],
        ['X X X', 'X X X', '[LYUK]', 'X X X', 'X X X'],
        ['X X X', 'X X X', 'X X X', '[LYUK]', 'X X X'],
        ['[LYUK]', 'X X X', 'X X X', 'X X X', '[LYUK]']
    ]
    t1_mask = Table(grid1_mask, colWidths=[27]*5, rowHeights=[24]*5)
    t1_mask.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#0f172a')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#94a3b8')),
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#ffffff')),
        ('BACKGROUND', (1,1), (1,1), colors.HexColor('#ffffff')),
        ('BACKGROUND', (2,2), (2,2), colors.HexColor('#ffffff')),
        ('BACKGROUND', (3,3), (3,3), colors.HexColor('#ffffff')),
        ('BACKGROUND', (0,4), (0,4), colors.HexColor('#ffffff')),
        ('BACKGROUND', (4,4), (4,4), colors.HexColor('#ffffff')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,-1), 'Arial-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#0f172a')),
    ]))

    badge_1 = Table([[Paragraph("TITKOS SZÓ:<br/><b>ÉL</b>", badge_style)]], colWidths=[110], rowHeights=[36])
    badge_1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0284c7')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))

    card1_left = [
        Paragraph("<b>1/A: ALAPKŐ BETŰRÁCS</b>", ParagraphStyle('H1a', fontName='Arial-Bold', fontSize=9.5, textColor=colors.HexColor('#0369a1'))),
        Spacer(1, 4),
        t1_grid,
        Spacer(1, 4),
        Paragraph("<i>Alapkarton (tasakba tenni)</i>", box_inst)
    ]
    card1_right = [
        Paragraph("<b>1/B: FEDŐSABLON (Vágd ki a fehér ablakokat!)</b>", ParagraphStyle('H1b', fontName='Arial-Bold', fontSize=9, textColor=colors.HexColor('#0369a1'))),
        Spacer(1, 4),
        t1_mask,
        Spacer(1, 4),
        Paragraph("<i>Illeszd a rácsra és olvasd le a szót!</i>", box_inst)
    ]

    card1_inner = Table([[card1_left, card1_right]], colWidths=[250, 275])
    card1_inner.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 0)
    ]))

    card1_full_content = [
        Table([[Paragraph("<b>1. ÁLLOMÁS (Lépcső alja) - AZ ALAPKŐ CARDAN-RÁCSA</b>", card_header_1), badge_1]], colWidths=[400, 125]),
        Spacer(1, 6),
        Paragraph("<i>„Keresd a szilárd támaszt a bejárat lépcsőinél!”</i> &nbsp;|&nbsp; <b>Feladat:</b> Illeszd a sablont az alapkartonra, és olvasd össze a megjelenő betűket!", body_style),
        Spacer(1, 8),
        card1_inner
    ]

    card1_container = Table([[card1_full_content]], colWidths=[547])
    card1_container.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 2, colors.HexColor('#0284c7')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0f9ff')),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    elements.append(card1_container)
    elements.append(Spacer(1, 14))

    # --- 2. ÁLLOMÁS ---
    badge_2 = Table([[Paragraph("TITKOS SZÓ:<br/><b>ŐK</b>", badge_style)]], colWidths=[110], rowHeights=[36])
    badge_2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ea580c')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))

    card2_full_content = [
        Table([[Paragraph("<b>2. ÁLLOMÁS (Tábortűz) - AZ OLTÁR HAMVA & FASZÉN-DÖRZSÖLŐS LAP</b>", card_header_2), badge_2]], colWidths=[400, 125]),
        Spacer(1, 6),
        Paragraph("<i>„Menj oda, ahol a tábor tüze lobog, és a felszálló füst az égre mutat!”</i>", body_style),
        Spacer(1, 4),
        Paragraph("<b>Instrukció a szervezőnek:</b> Írd rá erősen rányomott golyóstollal az <b>ÁLDOZAT</b> szót az alábbi fehér dobozba (hogy domború barázdák legyenek a papíron).<br/><b>A csapat feladata:</b> Vegyetek egy darab faszenet a tábortűzből (vagy egy ceruzát), és dörzsöljétek át a lapot, hogy a hamuból feltáruljon a titok!", body_style),
        Spacer(1, 8),
        Table([[Paragraph("<font color='#94a3b8' size='11'><b>[ ITT DÖRZSÖLD ÁT A FASZÉNNEL VAGY CERUZÁVAL ]</b></font>", ParagraphStyle('Pcenter2', fontName='Arial-Bold', alignment=1))]], colWidths=[525], rowHeights=[95], style=[
            ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#ea580c')),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ffffff')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ])
    ]

    card2_container = Table([[card2_full_content]], colWidths=[547])
    card2_container.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 2, colors.HexColor('#ea580c')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fff7ed')),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    elements.append(card2_container)

    # PAGE BREAK
    elements.append(PageBreak())

    # =========================================================================
    # PAGE 2: 3. ÁLLOMÁS & 4. ÁLLOMÁS
    # =========================================================================
    elements.append(Paragraph("TEMPLOM KINCSKERESŐ JÁTÉK - NYOMTATANDÓ KELLÉKEK (2. OLDAL)", title_style))
    elements.append(Paragraph("Vágd ki a kártyákat a külső színes keretek mentén, és helyezd el őket a megadott tábori helyszíneken!", sub_title_style))

    # --- 3. ÁLLOMÁS ---
    badge_3 = Table([[Paragraph("TITKOS SZÓ:<br/><b>ÖV</b>", badge_style)]], colWidths=[110], rowHeights=[36])
    badge_3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ca8a04')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))

    card3_full_content = [
        Table([[Paragraph("<b>3. ÁLLOMÁS (Lámpaoszlop a fák között) - A MENÓRA VILÁGOSSÁGA</b>", card_header_3), badge_3]], colWidths=[400, 125]),
        Spacer(1, 6),
        Paragraph("<i>„Keresd a lámpást a fák között, ami az éjszakai sötétségben utat mutat!”</i>", body_style),
        Spacer(1, 4),
        Paragraph("<b>Instrukció a szervezőnek:</b> Ennek a kártyának a <b>hátoldalára</b> vastag fekete filccel nagy betűkkel írd fel: <b>VILÁGOSSÁG</b>. Rögzítsd a kerti lámpaoszlopra!<br/><b>A csapat feladata:</b> Tartsátok ezt a lapot a lámpa fénye vagy a telefonotok vakuja felé, és olvassátok össze az átvilágító szót!", body_style),
        Spacer(1, 8),
        Table([[Paragraph("<font color='#854d0e' size='12'><b>* * * * [ TARTSD A LÁMPA FÉNYE VAGY A VAKU FELÉ! ] * * * *</b></font>", ParagraphStyle('Pcenter3', fontName='Arial-Bold', alignment=1))]], colWidths=[525], rowHeights=[95], style=[
            ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#ca8a04')),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fefce8')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ])
    ]

    card3_container = Table([[card3_full_content]], colWidths=[547])
    card3_container.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 2, colors.HexColor('#ca8a04')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fefce8')),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    elements.append(card3_container)
    elements.append(Spacer(1, 14))

    # --- 4. ÁLLOMÁS ---
    badge_4 = Table([[Paragraph("TITKOS SZÓ:<br/><b>EK</b>", badge_style)]], colWidths=[110], rowHeights=[36])
    badge_4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#7c3aed')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))

    # Large 26-letter Alphabet Scale Table
    alpha_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    t_alpha = Table([alpha_letters], colWidths=[20.1]*26, rowHeights=[22])
    t_alpha.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#7c3aed')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ffffff')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,-1), 'Arial-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#581c87')),
    ]))

    card4_full_content = [
        Table([[Paragraph("<b>4. ÁLLOMÁS (Nagyterem belső ajtaja) - A KETTÉHASADT KÁRPIT TITKA</b>", card_header_4), badge_4]], colWidths=[400, 125]),
        Spacer(1, 6),
        Paragraph("<i>„Keresd a legbelső ajtót a nagyterem végében, ahol a csend és az ima lakik!”</i>", body_style),
        Spacer(1, 4),
        Paragraph("<b>KÓDOLT SZENTÉLY-FELIRAT:</b>", ParagraphStyle('Sub4a', fontName='Arial-Bold', fontSize=9, textColor=colors.HexColor('#581c87'))),
        Spacer(1, 2),
        Table([[Paragraph("<font color='#581c87' size='14'><b>T - A - F - O - U - F - L &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; T - A - F - O - U - K - F</b></font>", ParagraphStyle('PcodeBig', fontName='Arial-Bold', alignment=1))]], colWidths=[525], rowHeights=[36], style=[
            ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#7c3aed')),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#faf5ff')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]),
        Spacer(1, 6),
        Paragraph("<b>KÓDFEJTŐ ÁBÉCÉ SKÁLA:</b>", ParagraphStyle('SubAlpha', fontName='Arial-Bold', fontSize=8.5, textColor=colors.HexColor('#6b21a8'))),
        Spacer(1, 2),
        t_alpha,
        Spacer(1, 5),
        Paragraph("<b>Kódfejtő szabály:</b> <i>„A kárpit felülről az aljáig kettéhasadt! Lépj a fenti ábécé skálán minden kódolt betűvel <b>1-gyel BALRA</b> (visszafelé)! Az <b>A</b> betűnél a skála körbefordul: <b>A -> Z</b>!”</i>", body_style)
    ]

    card4_container = Table([[card4_full_content]], colWidths=[547])
    card4_container.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 2, colors.HexColor('#7c3aed')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#faf5ff')),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    elements.append(card4_container)

    doc.build(elements)
    print(f"Sikeresen legenerálva: {pdf_path}")

if __name__ == "__main__":
    create_templom_pdf()
