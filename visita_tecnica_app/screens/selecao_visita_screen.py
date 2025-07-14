from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class SelecaoVisitaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        layout.add_widget(Label(text="Selecione o tipo de visita", font_size=24))

        btn_visita_tecnica = Button(text="Visita Técnica", size_hint_y=None, height=60)
        btn_visita_tecnica.bind(on_press=lambda x: setattr(self.manager, 'current', 'nova_visita'))

        btn_visita_fsc = Button(text="Visita FSC", size_hint_y=None, height=60)
        btn_visita_fsc.bind(on_press=lambda x: setattr(self.manager, 'current', 'visita_fsc'))

        btn_voltar = Button(text="Voltar", size_hint_y=None, height=60)
        btn_voltar.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))

        layout.add_widget(btn_visita_tecnica)
        layout.add_widget(btn_visita_fsc)
        layout.add_widget(btn_voltar)

        self.add_widget(layout)
