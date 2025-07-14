from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.app import App

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', spacing=20, padding=40)

        layout.add_widget(Label(text='Menu Principal', font_size=24, size_hint_y=None, height=60))

        # Botão para a tela de seleção de tipo de visita
        btn_nova_visita = Button(text='Nova Visita', size_hint_y=None, height=60)
        btn_nova_visita.bind(on_press=self.abrir_selecao_visita)
        layout.add_widget(btn_nova_visita)

        # Botão para o histórico
        btn_historico = Button(text='Histórico de Visitas', size_hint_y=None, height=60)
        btn_historico.bind(on_press=self.historico)
        layout.add_widget(btn_historico)

        # Botão para estatísticas
        btn_estatisticas = Button(text='Estatísticas', size_hint_y=None, height=60)
        btn_estatisticas.bind(on_press=self.estatisticas)
        layout.add_widget(btn_estatisticas)

        # Botão para sair
        btn_sair = Button(text='Sair', size_hint_y=None, height=60)
        btn_sair.bind(on_press=self.sair)
        layout.add_widget(btn_sair)

        self.add_widget(layout)

    def abrir_selecao_visita(self, instance):
        self.manager.current = 'selecao_visita'

    def historico(self, instance):
        try:
            self.manager.get_screen('historico').atualizar_historico()
        except Exception as e:
            print(f"Erro ao atualizar histórico: {e}")
        self.manager.current = 'historico'

    def estatisticas(self, instance):
        try:
            self.manager.get_screen('estatisticas').atualizar_estatisticas()
        except Exception as e:
            print(f"Erro ao atualizar estatísticas: {e}")
        self.manager.current = 'estatisticas'

    def sair(self, instance):
        app = App.get_running_app()
        app.usuario_logado = None
        self.manager.current = 'login'
