from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from database.db_manager import DBManager
import os

class DetalhesVisitaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DBManager()
        self.visita_id = None
        self.tela_anterior = 'menu'

    def carregar_detalhes(self, visita_id):
        self.visita_id = visita_id
        self.clear_widgets()

        visita = self.db.obter_visita_por_id(visita_id)

        layout = GridLayout(cols=1, padding=10, spacing=5, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        for k in ['produtor', 'propriedade', 'municipio', 'tecnico', 'data', 'chegada', 'saida', 'estimulo_intervalo', 'estimulo_conc']:
            layout.add_widget(Label(text=f"{k.capitalize()}: {visita.get(k, '')}", size_hint_y=None, height=30))

        layout.add_widget(Label(text=f"Divisão de Tarefa: {'Sim' if visita['divisao_tarefa'] else 'Não'}", size_hint_y=None, height=30))
        layout.add_widget(Label(text=f"Borracha no Chão: {'Sim' if visita['borracha_chao'] else 'Não'}", size_hint_y=None, height=30))

        layout.add_widget(Label(text="Manutenção:", size_hint_y=None, height=30))
        for key, val in visita["manutencao"].items():
            layout.add_widget(Label(text=f" - {key}: {'Sim' if val else 'Não'}", size_hint_y=None, height=30))

        # Mostrar coordenadas GPS
        lat = visita.get('latitude')
        lon = visita.get('longitude')
        layout.add_widget(Label(text=f"Latitude: {lat if lat is not None else 'N/A'}", size_hint_y=None, height=30))
        layout.add_widget(Label(text=f"Longitude: {lon if lon is not None else 'N/A'}", size_hint_y=None, height=30))

        # Exibir imagem
        img_path = None
        if visita.get("foto_path"):
            img_path = os.path.join(os.path.dirname(__file__), visita["foto_path"])
        if img_path and os.path.exists(img_path):
            layout.add_widget(Image(source=img_path, size_hint_y=None, height=200, allow_stretch=True, keep_ratio=True))
        else:
            layout.add_widget(Label(text="Foto não encontrada.", size_hint_y=None, height=30))

        btn_pdf = Button(text="Exportar PDF", size_hint_y=None, height=50)
        btn_pdf.bind(on_press=self.exportar_pdf)
        layout.add_widget(btn_pdf)

        btn_voltar = Button(text="Voltar", size_hint_y=None, height=50)
        btn_voltar.bind(on_press=lambda x: setattr(self.manager, 'current', self.tela_anterior))
        layout.add_widget(btn_voltar)

        scroll = ScrollView()
        scroll.add_widget(layout)
        self.add_widget(scroll)

    def exportar_pdf(self, instance):
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Image as PDFImage, Spacer
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        import os

        visita = self.db.obter_visita_por_id(self.visita_id)
        styles = getSampleStyleSheet()
        story = []

        for k in ['produtor', 'propriedade', 'municipio', 'tecnico', 'data', 'chegada', 'saida', 'estimulo_intervalo', 'estimulo_conc']:
            story.append(Paragraph(f"{k.capitalize()}: {visita.get(k, '')}", styles['Normal']))
            story.append(Spacer(1, 6))

        story.append(Paragraph(f"Divisão de Tarefa: {'Sim' if visita['divisao_tarefa'] else 'Não'}", styles['Normal']))
        story.append(Paragraph(f"Borracha no Chão: {'Sim' if visita['borracha_chao'] else 'Não'}", styles['Normal']))

        story.append(Spacer(1, 10))
        story.append(Paragraph("Manutenção:", styles['Heading3']))
        for key, val in visita["manutencao"].items():
            story.append(Paragraph(f"{key}: {'Sim' if val else 'Não'}", styles['Normal']))

        # Coordenadas GPS e link para Google Maps
        latitude = visita.get('latitude')
        longitude = visita.get('longitude')
        if latitude and longitude:
            maps_url = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
            story.append(Spacer(1, 10))
            story.append(Paragraph(f"Latitude: {latitude}", styles['Normal']))
            story.append(Paragraph(f"Longitude: {longitude}", styles['Normal']))
            story.append(Paragraph(f"<a href='{maps_url}'>Abrir localização no Google Maps</a>", styles['Normal']))
        else:
            story.append(Spacer(1, 10))
            story.append(Paragraph("Coordenadas GPS não disponíveis.", styles['Normal']))

        # Imagem
        img_path = None
        if visita.get("foto_path"):
            img_path = os.path.join(os.path.dirname(__file__), visita["foto_path"])

        if img_path and os.path.exists(img_path):
            max_width = 4 * inch
            max_height = 3 * inch
            story.append(Spacer(1, 20))
            img = PDFImage(img_path)
            # Ajustar tamanho da imagem proporcionalmente ao max
            img.drawWidth = max_width
            img.drawHeight = max_height
            story.append(img)
        else:
            story.append(Paragraph("Nenhuma foto disponível.", styles['Normal']))

        output_path = os.path.expanduser(f"~/Downloads/visita_{self.visita_id}.pdf")
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        doc.build(story)
