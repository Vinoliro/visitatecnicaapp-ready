from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from database.db_manager import DBManager
import re

class CadastroScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DBManager()

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        self.nome = TextInput(hint_text="Nome completo", multiline=False)
        self.email = TextInput(hint_text="Email", multiline=False)
        self.senha = TextInput(hint_text="Senha", password=True, multiline=False)

        cadastrar_btn = Button(text="Cadastrar", on_press=self.cadastrar_usuario)
        voltar_btn = Button(text="Voltar", on_press=self.voltar_login)

        layout.add_widget(Label(text="Cadastro", font_size=24))
        layout.add_widget(self.nome)
        layout.add_widget(self.email)
        layout.add_widget(self.senha)
        layout.add_widget(cadastrar_btn)
        layout.add_widget(voltar_btn)

        self.add_widget(layout)

    def cadastrar_usuario(self, instance):
        nome = self.nome.text.strip()
        email = self.email.text.strip()
        senha = self.senha.text.strip()

        if not nome or not email or not senha:
            self.mostrar_popup("Erro", "Preencha todos os campos")
            return

        if not self.validar_email(email):
            self.mostrar_popup("Erro", "Email inválido")
            return

        sucesso = self.db.cadastrar_usuario(nome, email, senha)
        if sucesso:
            self.mostrar_popup("Sucesso", "Usuário cadastrado com sucesso")
            # Limpar campos
            self.nome.text = ""
            self.email.text = ""
            self.senha.text = ""
            self.manager.current = 'login'
        else:
            self.mostrar_popup("Erro", "Email já cadastrado")

    def voltar_login(self, instance):
        self.manager.current = 'login'

    def mostrar_popup(self, titulo, mensagem):
        popup = Popup(title=titulo, content=Label(text=mensagem), size_hint=(0.6, 0.4))
        popup.open()

    def validar_email(self, email):
        # Validação simples de email
        regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        return re.match(regex, email) is not None
