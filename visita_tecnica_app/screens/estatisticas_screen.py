from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image as KivyImage
from kivy.uix.label import Label
from kivy.graphics.texture import Texture

from database.db_manager import DBManager
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
from datetime import datetime
from collections import Counter

import logging
logging.getLogger('matplotlib').setLevel(logging.WARNING)

class EstatisticasScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DBManager()
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.add_widget(self.layout)
        self.atualizar_estatisticas()

    def atualizar_estatisticas(self):
        self.layout.clear_widgets()
        visitas = self.db.obter_todas_visitas()

        if not visitas:
            self.layout.add_widget(Label(text="Nenhuma visita registrada"))
            return

        # GRÁFICO 1: Manutenções - proporção dos problemas encontrados
        manutencao_total = Counter()
        for v in visitas:
            manutencao = v.get("manutencao", {})
            for tipo, ativo in manutencao.items():
                if ativo:
                    manutencao_total[tipo] += 1

        if manutencao_total:
            fig1, ax1 = plt.subplots()
            ax1.pie(manutencao_total.values(), labels=manutencao_total.keys(), autopct='%1.1f%%', startangle=90)
            ax1.set_title("Proporção de Problemas Encontrados (Manutenções Ativas)")
            ax1.axis('equal')
            self.layout.add_widget(self._figura_para_imagem(fig1))

        # GRÁFICO 2: Visitas por mês
        datas = []
        for v in visitas:
            try:
                data = datetime.strptime(v.get('data', ''), "%Y-%m-%d")
                datas.append(data.strftime("%Y-%m"))
            except Exception:
                continue

        contagem_meses = Counter(datas)
        if contagem_meses:
            meses_ordenados = sorted(contagem_meses.items())
            meses, quantidades = zip(*meses_ordenados)
            fig2, ax2 = plt.subplots()
            ax2.bar(meses, quantidades, color='skyblue')
            ax2.set_ylabel("Visitas")
            ax2.set_title("Visitas por Mês")
            ax2.tick_params(axis='x', rotation=45)
            self.layout.add_widget(self._figura_para_imagem(fig2))

        # Top 3 técnicos com mais visitas
        tecnicos = [v.get("tecnico", "").strip() for v in visitas if v.get("tecnico")]
        contagem_tecnicos = Counter(tecnicos)
        if contagem_tecnicos:
            top_tecnicos = contagem_tecnicos.most_common(3)
            top_texto = "Top 3 Técnicos com Mais Visitas:\n"
            for i, (nome, total) in enumerate(top_tecnicos, start=1):
                top_texto += f"{i}. {nome} - {total} visitas\n"

            label = Label(
                text=top_texto.strip(),
                size_hint_y=None,
                height=120
            )
            self.layout.add_widget(label)

        # Botão voltar
        btn_voltar = Button(text="Voltar ao Menu", size_hint_y=None, height=60)
        btn_voltar.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        self.layout.add_widget(btn_voltar)

    def _figura_para_imagem(self, fig):
        buf = io.BytesIO()
        fig.tight_layout()
        fig.savefig(buf, format='png')
        buf.seek(0)
        plt.close(fig)

        image = KivyImage()
        image.texture = self._buffer_para_texture(buf)
        buf.close()
        return image

    def _buffer_para_texture(self, buf):
        from PIL import Image as PILImage
        pil_image = PILImage.open(buf).convert('RGBA')
        texture = Texture.create(size=pil_image.size)
        texture.blit_buffer(pil_image.tobytes(), colorfmt='rgba', bufferfmt='ubyte')
        texture.flip_vertical()
        return texture
