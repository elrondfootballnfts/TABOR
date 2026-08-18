import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def register_unicode_fonts():
    # Register Arial fonts for Hungarian accents
    font_paths = {
        'Arial': 'C:/Windows/Fonts/arial.ttf',
        'Arial-Bold': 'C:/Windows/Fonts/arialbd.ttf',
        'Arial-Italic': 'C:/Windows/Fonts/ariali.ttf'
    }
    for font_name, path in font_paths.items():
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont(font_name, path))

def create_templom_pdf():
    register_unicode_fonts()
    pdf_path = "TEMPLOM_Nyomtatando_Kartyak.pdf"
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
        fontName='Arial-Bold',
        fontSize=17,
        leading=21,
        textColor=colors.HexColor('#0f172a'),
        alignment=1,
        spaceAfter=8
    )
    card_title_1 = ParagraphStyle(
        'CardTitle1',
        fontName='Arial-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#0369a1'),
        spaceAfter=4
    )
    card_title_2 = ParagraphStyle(
        'CardTitle2',
        fontName='Arial-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#c2410c'),
        spaceAfter=4
    )
    card_title_3 = ParagraphStyle(
        'CardTitle3',
        fontName='Arial-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#a16207'),
        spaceAfter=4
    )
    card_title_4 = ParagraphStyle(
        'CardTitle4',
        fontName='Arial-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#6b21a8'),
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'BodyDark',
        fontName='Arial',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#334155')
    )
    box_inst = ParagraphStyle(
        'BoxInst',
        fontName='Arial-Italic',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#475569')
    )
    corner_word_style = ParagraphStyle(
        'CornerWord',
        fontName='Arial-Bold',
        fontSize=11,
        leading=13,
        textColor=colors.HexColor('#ffffff'),
        alignment=1
    )

    elements = []

    # Title & Introduction
    elements.append(Paragraph("TEMPLOM JÁTÉK - NYOMTATHATÓ TEREPI KELLÉKEK", title_style))
    elements.append(Paragraph("<b>Használati útmutató:</b> Vágd ki a 4 állomás kártyáit és sablonjait a keretek mentén, és helyezd el őket a megadott helyszíneken!", body_style))
    elements.append(Spacer(1, 10))

    # =========================================================================
    # 1. ÁLLOMÁS: AZ ALAPKŐ (Cardan-rács & Ablakos sablon)
    # =========================================================================
    elements.append(Paragraph("1. ÁLLOMÁS (Lépcső alja) - CARDAN-RÁCS & ABLAKOS SABLON", card_title_1))
    elements.append(Paragraph("<i>Instrukció a szervezőnek:</i> Vágd ki az <b>1/A Alapkártyát</b> és az <b>1/B Fedősablont</b>. Az 1/B sablonon vágd ki a fehér [LYUK] ablakokat! Tedd a kettőt egy tasakba a lépcsőnél.", box_inst))
    elements.append(Spacer(1, 5))

    grid1_data = [
        ['A', 'R', 'T', 'Z', 'M'],
        ['B', 'L', 'K', 'D', 'P'],
        ['S', 'N', 'A', 'V', 'G'],
        ['E', 'F', 'H', 'P', 'J'],
        ['K', 'U', 'W', 'Y', 'Ő']
    ]
    t1_grid = Table(grid1_data, colWidths=[24]*5, rowHeights=[19]*5)
    t1_grid.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#64748b')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,-1), 'Arial-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 11),
    ]))

    grid1_mask = [
        ['[LYUK]', 'X X X', 'X X X', 'X X X', 'X X X'],
        ['X X X', '[LYUK]', 'X X X', 'X X X', 'X X X'],
        ['X X X', 'X X X', '[LYUK]', 'X X X', 'X X X'],
        ['X X X', 'X X X', 'X X X', '[LYUK]', 'X X X'],
        ['[LYUK]', 'X X X', 'X X X', 'X X X', '[LYUK]']
    ]
    t1_mask = Table(grid1_mask, colWidths=[24]*5, rowHeights=[19]*5)
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
        ('FONTNAME', (0,0), (-1,-1), 'Arial'),
        ('FONTSIZE', (0,0), (-1,-1), 6.5),
    ]))

    badge_el = Table([[Paragraph("TITKOS SZÓ:<br/><b>ÉL</b>", corner_word_style)]], colWidths=[90], rowHeights=[28])
    badge_el.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0284c7')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))

    card1_left = [
        Paragraph("<b>1/A: ALAPKŐ BETŰRÁCS</b>", ParagraphStyle('H1a', fontName='Arial-Bold', fontSize=8.5, textColor=colors.HexColor('#0369a1'))),
        Spacer(1, 4),
        t1_grid,
        Spacer(1, 4),
        Paragraph("<i>Alapkarton</i>", box_inst)
    ]
    card1_right = [
        Paragraph("<b>1/B: FEDŐSABLON (Vágd ki a fehér lyukakat!)</b>", ParagraphStyle('H1b', fontName='Arial-Bold', fontSize=8, textColor=colors.HexColor('#0369a1'))),
        Spacer(1, 4),
        t1_mask,
        Spacer(1, 6),
        badge_el
    ]

    card1_table = Table([[card1_left, card1_right]], colWidths=[240, 280])
    card1_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#0284c7')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f0f9ff')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    elements.append(card1_table)
    elements.append(Spacer(1, 14))

    # =========================================================================
    # 2. ÁLLOMÁS: AZ OLTÁR FÜSTJE (Faszén-dörzsölős titkos lap)
    # =========================================================================
    elements.append(Paragraph("2. ÁLLOMÁS (Tábortűz) - FASZÉN-DÖRZSÖLŐS TITKOS LAP", card_title_2))
    elements.append(Paragraph("<i>Instrukció a szervezőnek:</i> Írd rá erősen rányomott golyóstollal az <b>ÁLDOZAT</b> szót a középső fehér keretbe. A gyerekek faszénnel dörzsölik át!", box_inst))
    elements.append(Spacer(1, 5))

    badge_ok = Table([[Paragraph("TITKOS SZÓ:<br/><b>ŐK</b>", corner_word_style)]], colWidths=[90], rowHeights=[28])
    badge_ok.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ea580c')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))

    card2_content = [
        Paragraph("<b>2. ÁLLOMÁS - AZ OLTÁR HAMVA</b>", ParagraphStyle('H2c', fontName='Arial-Bold', fontSize=10.5, textColor=colors.HexColor('#9a3412'))),
        Spacer(1, 3),
        Paragraph("<i>„Végy egy darabka faszenet a tábortűzből (vagy egy ceruzát), és finoman dörzsöld át ezt a fehér mezőt, hogy a hamuból feltáruljon a titok!”</i>", body_style),
        Spacer(1, 6),
        Table([[Paragraph("<font color='#94a3b8'>[ ITT DÖRZSÖLD ÁT A FASZÉNNEL ]</font>", ParagraphStyle('Pcenter', fontName='Arial-Italic', fontSize=9, alignment=1))]], colWidths=[380], rowHeights=[45], style=[
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#94a3b8')),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ffffff')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]),
        Spacer(1, 6),
        badge_ok
    ]

    card2_table = Table([[card2_content]], colWidths=[520])
    card2_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#ea580c')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fff7ed')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    elements.append(card2_table)

    elements.append(PageBreak())

    # =========================================================================
    # 3. ÁLLOMÁS: A MENÓRA VILÁGOSSÁGA (Átvilágítós lámpás lap)
    # =========================================================================
    elements.append(Paragraph("3. ÁLLOMÁS (Lámpaoszlop) - ÁTVILÁGÍTÓS LÁMPÁS LAP", card_title_3))
    elements.append(Paragraph("<i>Instrukció a szervezőnek:</i> Ennek a kártyának a <b>hátoldalára</b> vastag fekete filccel írd fel: <b>VILÁGOSSÁG</b>. Ragaszd a kerti lámpaoszlopra!", box_inst))
    elements.append(Spacer(1, 5))

    badge_ov = Table([[Paragraph("TITKOS SZÓ:<br/><b>ÖV</b>", corner_word_style)]], colWidths=[90], rowHeights=[28])
    badge_ov.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ca8a04')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))

    card3_content = [
        Paragraph("<b>3. ÁLLOMÁS - A MENÓRA VILÁGOSSÁGA</b>", ParagraphStyle('H3c', fontName='Arial-Bold', fontSize=10.5, textColor=colors.HexColor('#854d0e'))),
        Spacer(1, 3),
        Paragraph("<i>„Keresd a világosság forrását! Tartsd ezt a lapot a LÁMPA FÉNYE vagy a MOBILOD VAKUJA felé, és olvasd össze az átvilágító szót!”</i>", body_style),
        Spacer(1, 6),
        Table([[Paragraph("<font color='#854d0e'><b>* * * * [ TARTSD A LÁMPAFÉNY FELÉ! ] * * * *</b></font>", ParagraphStyle('Pcenter3', fontName='Arial-Bold', fontSize=9, alignment=1))]], colWidths=[380], rowHeights=[45], style=[
            ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#ca8a04')),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fefce8')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]),
        Spacer(1, 6),
        badge_ov
    ]

    card3_table = Table([[card3_content]], colWidths=[520])
    card3_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#ca8a04')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fefce8')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    elements.append(card3_table)
    elements.append(Spacer(1, 14))

    # =========================================================================
    # 4. ÁLLOMÁS: A HASADT KÁRPIT (Cézár-titkosírás a Szentek Szentjéhez)
    # =========================================================================
    elements.append(Paragraph("4. ÁLLOMÁS (Nagyterem belső ajtaja) - CÉZÁR-TITKOSÍRÁS", card_title_4))
    elements.append(Paragraph("<i>Instrukció a szervezőnek:</i> Rögzítsd a nagyterem/imaszoba legbelső ajtajára.", box_inst))
    elements.append(Spacer(1, 5))

    badge_ek = Table([[Paragraph("TITKOS SZÓ:<br/><b>EK</b>", corner_word_style)]], colWidths=[90], rowHeights=[28])
    badge_ek.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#7c3aed')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))

    card4_content = [
        Paragraph("<b>4. ÁLLOMÁS - A KETTÉHASADT KÁRPIT TITKA</b>", ParagraphStyle('H4c', fontName='Arial-Bold', fontSize=10.5, textColor=colors.HexColor('#581c87'))),
        Spacer(1, 3),
        Paragraph("KÓDOLT SZÖVEG:", ParagraphStyle('Sub4', fontName='Arial-Bold', fontSize=8.5, textColor=colors.HexColor('#581c87'))),
        Spacer(1, 2),
        Table([[Paragraph("<font color='#581c87'><b>T - A - F - O - U - F - L &nbsp;&nbsp;&nbsp; T - A - F - O - U - K - F</b></font>", ParagraphStyle('Pcode', fontName='Arial-Bold', fontSize=11, alignment=1))]], colWidths=[380], rowHeights=[26], style=[
            ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#7c3aed')),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#faf5ff')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]),
        Spacer(1, 5),
        Paragraph("Kulcs: <i>„A kárpit felülről az aljáig kettéhasadt! Lépj MINDEN betűvel EGGYEL VISSZA az ábécében: T -> S, A -> Z, F -> E, O -> N, U -> T, L -> K, K -> J!”</i>", body_style),
        Spacer(1, 6),
        badge_ek
    ]

    card4_table = Table([[card4_content]], colWidths=[520])
    card4_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#7c3aed')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#faf5ff')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    elements.append(card4_table)

    doc.build(elements)
    print(f"Sikeresen legenerálva: {pdf_path}")

if __name__ == "__main__":
    create_templom_pdf()
