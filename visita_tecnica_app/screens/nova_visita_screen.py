from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from plyer import gps
from datetime import datetime
from database.db_manager import DBManager
from kivy.app import App  # Import necessário para pegar app atual

class NovaVisitaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DBManager()
        self.campos = {}
        self.checkboxes = {}
        self.foto_path = ''
        self.latitude = ''
        self.longitude = ''

        layout = GridLayout(cols=1, padding=20, spacing=20, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        for campo in [
            "produtor", "propriedade", "municipio", "tecnico", "data",
            "chegada", "saida", "estimulo_intervalo", "estimulo_conc"
        ]:
            box = BoxLayout(orientation='vertical', size_hint_y=None, height=120)
            box.add_widget(Label(text=campo.capitalize(), size_hint_y=None, height=40))
            ti = TextInput(multiline=False, size_hint_y=None, height=60)
            box.add_widget(ti)
            layout.add_widget(box)
            self.campos[campo] = ti

        for campo in ["divisao_tarefa", "borracha_chao"]:
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=80)
            cb = CheckBox(size_hint=(None, None), size=(50, 50))
            box.add_widget(cb)
            box.add_widget(Label(text=campo.replace("_", " ").capitalize()))
            layout.add_widget(box)
            self.campos[campo] = cb

        manutencao_tit = Label(text="Manutenção:", bold=True, size_hint_y=None, height=40)
        layout.add_widget(manutencao_tit)

        for item in [
            "Controle de Doenças", "Controle de Pragas", "Limpeza nas Linhas",
            "Limpeza nas Entrelinhas", "Traçagem de Consumo"
        ]:
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=80)
            cb = CheckBox(size_hint=(None, None), size=(50, 50))
            box.add_widget(cb)
            box.add_widget(Label(text=item))
            layout.add_widget(box)
            self.checkboxes[item] = cb

        btn_foto = Button(text="Selecionar Foto", size_hint_y=None, height=60)
        btn_foto.bind(on_press=self.selecionar_foto)
        layout.add_widget(btn_foto)

        btn_salvar = Button(text="Salvar Visita", size_hint_y=None, height=60)
        btn_salvar.bind(on_press=self.salvar_visita)
        layout.add_widget(btn_salvar)

        btn_voltar = Button(text="Voltar ao Menu", size_hint_y=None, height=60)
        btn_voltar.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_voltar)

        scroll = ScrollView()
        scroll.add_widget(layout)
        self.add_widget(scroll)

    def selecionar_foto(self, instance):
        chooser = FileChooserIconView()

        def selecionar(chooser, selection, touch=None):
            if selection:
                self.foto_path = selection[0]
                self.obter_gps()
                popup.dismiss()

        chooser.bind(on_submit=selecionar)

        popup = Popup(title="Selecionar Foto", content=chooser, size_hint=(0.9, 0.9))
        popup.open()

    def obter_gps(self):
        try:
            gps.configure(on_location=self.on_location, on_status=self.on_status)
            gps.start(minTime=1000, minDistance=0)
        except NotImplementedError:
            print("GPS não suportado nesta plataforma")

    def on_location(self, **kwargs):
        self.latitude = str(kwargs.get('lat', ''))
        self.longitude = str(kwargs.get('lon', ''))
        gps.stop()

    def on_status(self, stype, status):
        print(f"[GPS] {stype} = {status}")

    def salvar_visita(self, instance):
        dados = {}
        for k, v in self.campos.items():
            if isinstance(v, TextInput):
                if k == 'data':
                    try:
                        data_obj = datetime.strptime(v.text, "%d/%m/%Y")
                        dados[k] = data_obj.strftime("%Y-%m-%d")
                    except ValueError:
                        print("❌ Data inválida. Use o formato DD/MM/AAAA.")
                        return
                else:
                    dados[k] = v.text
            elif isinstance(v, CheckBox):
                dados[k] = v.active

        dados['manutencao'] = {chave: cb.active for chave, cb in self.checkboxes.items()}
        dados['foto_path'] = self.foto_path
        dados['latitude'] = self.latitude
        dados['longitude'] = self.longitude

        # Correção: pegar o app atual para acessar usuario_logado
        app = App.get_running_app()
        usuario_logado = getattr(app, 'usuario_logado', None)
        usuario_id = usuario_logado['id'] if usuario_logado else None

        self.db.inserir_visita(dados, usuario_id=usuario_id)
        print("✅ Visita salva com sucesso")
        self.manager.current = 'menu'
