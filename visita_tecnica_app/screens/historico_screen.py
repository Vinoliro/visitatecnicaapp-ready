from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.app import App
from database.db_manager import DBManager

class HistoricoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DBManager()

        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Filtros
        filtros_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)

        self.produtor_input = TextInput(hint_text="Produtor", multiline=False)
        self.municipio_input = TextInput(hint_text="Município", multiline=False)
        self.data_inicio_input = TextInput(hint_text="Data Início (DD/MM/AAAA)", multiline=False)
        self.data_fim_input = TextInput(hint_text="Data Fim (DD/MM/AAAA)", multiline=False)

        filtros_layout.add_widget(self.produtor_input)
        filtros_layout.add_widget(self.municipio_input)
        filtros_layout.add_widget(self.data_inicio_input)
        filtros_layout.add_widget(self.data_fim_input)

        btn_filtrar = Button(text="Filtrar", size_hint_x=None, width=100)
        btn_filtrar.bind(on_press=self.atualizar_historico)
        filtros_layout.add_widget(btn_filtrar)

        main_layout.add_widget(filtros_layout)

        # Label título
        main_layout.add_widget(Label(text='Histórico de Visitas', size_hint_y=None, height=40))

        # Scroll com visitas
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        main_layout.add_widget(self.scroll)

        # Botão voltar
        voltar_btn = Button(text='Voltar', size_hint_y=None, height=50)
        voltar_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        main_layout.add_widget(voltar_btn)

        self.add_widget(main_layout)

    def atualizar_historico(self, *args):
        self.grid.clear_widgets()

        try:
            usuario_logado = App.get_running_app().usuario_logado
        except AttributeError:
            usuario_logado = None

        if not usuario_logado:
            self.grid.add_widget(Label(text="⚠️ Usuário não autenticado."))
            return

        produtor = self.produtor_input.text.strip()
        municipio = self.municipio_input.text.strip()
        data_inicio = self.data_inicio_input.text.strip()
        data_fim = self.data_fim_input.text.strip()

        visitas = self.db.listar_visitas_filtradas(
            produtor=produtor,
            municipio=municipio,
            data_inicio=data_inicio,
            data_fim=data_fim,
            usuario_id=usuario_logado["id"]
        )

        if not visitas:
            self.grid.add_widget(Label(text="Nenhuma visita encontrada."))
            return

        for visita in visitas:
            box = BoxLayout(orientation='vertical', size_hint_y=None, height=150)
            info = f"{visita['data']} - {visita['produtor']} - {visita['municipio']}"
            box.add_widget(Label(text=info, halign="left", valign="middle"))
            btn_detalhes = Button(text="Ver Detalhes", size_hint_y=None, height=40)
            btn_detalhes.bind(on_press=lambda x, id=visita['id']: self.ver_detalhes(id))
            box.add_widget(btn_detalhes)
            self.grid.add_widget(box)

    def ver_detalhes(self, visita_id):
        detalhes_screen = self.manager.get_screen('detalhes_visita')
        detalhes_screen.carregar_detalhes(visita_id)
        self.manager.current = 'detalhes_visita'
