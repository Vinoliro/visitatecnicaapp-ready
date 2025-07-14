from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.app import App  # Import necessário para acessar o App principal
from database.db_manager import DBManager

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DBManager()

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        self.email = TextInput(hint_text="Email", multiline=False)
        self.senha = TextInput(hint_text="Senha", password=True, multiline=False)

        login_btn = Button(text="Login", on_press=self.fazer_login)
        cadastro_btn = Button(text="Cadastrar novo usuário", on_press=self.ir_para_cadastro)

        layout.add_widget(Label(text="Login", font_size=24))
        layout.add_widget(self.email)
        layout.add_widget(self.senha)
        layout.add_widget(login_btn)
        layout.add_widget(cadastro_btn)

        self.add_widget(layout)

    def fazer_login(self, instance):
        email = self.email.text.strip()
        senha = self.senha.text.strip()

        if not email or not senha:
            self.mostrar_popup("Erro", "Preencha email e senha")
            return

        usuario = self.db.autenticar_usuario(email, senha)
        if usuario:
            # Salvar usuário logado no app principal
            App.get_running_app().usuario_logado = usuario

            # Limpar campos
            self.email.text = ""
            self.senha.text = ""

            self.manager.current = 'menu'
        else:
            self.mostrar_popup("Erro", "Credenciais inválidas")

    def ir_para_cadastro(self, instance):
        self.manager.current = 'cadastro'

    def mostrar_popup(self, titulo, mensagem):
        popup = Popup(
            title=titulo,
            content=Label(text=mensagem),
            size_hint=(0.6, 0.4)
        )
        popup.open()
