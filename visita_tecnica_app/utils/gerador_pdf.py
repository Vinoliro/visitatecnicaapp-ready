import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER

def gerar_pdf_fsc(dados, caminho_arquivo):
    doc = SimpleDocTemplate(caminho_arquivo, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    estilos_custom = {
        'titulo': ParagraphStyle('titulo', parent=styles['Title'], alignment=TA_CENTER, spaceAfter=12),
        'cabecalho': ParagraphStyle('cabecalho', parent=styles['Heading2'], alignment=TA_LEFT, spaceAfter=8),
        'normal': styles['Normal'],
        'italico': ParagraphStyle('italico', parent=styles['Normal'], fontName='Helvetica-Oblique'),
    }

    story = []

    # Título do relatório
    story.append(Paragraph("Relatório de Visita FSC", estilos_custom['titulo']))

    # Dados básicos
    campos = [
        ("Data", dados.get("data", "")),
        ("Produtor", dados.get("produtor", "")),
        ("Nome da Fazenda", dados.get("propriedade", "")),
        ("Hora de Chegada", dados.get("chegada", "")),
        ("Hora de Saída", dados.get("saida", "")),
    ]
    for campo, valor in campos:
        story.append(Paragraph(f"<b>{campo}:</b> {valor}", estilos_custom['normal']))

    story.append(Spacer(1, 12))

    # Checklist
    story.append(Paragraph("Checklist:", estilos_custom['cabecalho']))
    checklist = dados.get("checklist", {})
    for item, marcado in checklist.items():
        status = "Sim" if marcado else "Não"
        story.append(Paragraph(f"- {item}: {status}", estilos_custom['normal']))
    outros = dados.get("outros", "")
    if outros:
        story.append(Paragraph(f"<b>Outros:</b> {outros}", estilos_custom['normal']))

    story.append(Spacer(1, 12))

    # Fotos com observações
    fotos = dados.get("fotos", [])
    if fotos:
        story.append(Paragraph("Fotos com Observações:", estilos_custom['cabecalho']))
        for foto in fotos:
            caminho = foto.get("caminho")
            observacao = foto.get("observacao", "")

            if caminho and os.path.isfile(caminho):
                try:
                    img = Image(caminho)
                    # Redimensionar para caber no PDF (mantendo proporção)
                    max_width = 14 * cm
                    max_height = 10 * cm
                    img.drawWidth, img.drawHeight = scale_image(img.imageWidth, img.imageHeight, max_width, max_height)
                    story.append(img)
                    story.append(Paragraph(f"<i>Observação:</i> {observacao}", estilos_custom['italico']))
                    story.append(Spacer(1, 12))
                except Exception as e:
                    story.append(Paragraph(f"Erro ao carregar imagem '{os.path.basename(caminho)}': {e}", estilos_custom['normal']))
            else:
                story.append(Paragraph(f"Imagem não encontrada: {caminho}", estilos_custom['normal']))
    else:
        story.append(Paragraph("Nenhuma foto adicionada.", estilos_custom['normal']))

    doc.build(story)

def scale_image(orig_width, orig_height, max_width, max_height):
    """
    Calcula a largura e altura da imagem para manter proporção dentro dos limites máximos.
    """
    ratio = min(max_width / orig_width, max_height / orig_height)
    return orig_width * ratio, orig_height * ratio
