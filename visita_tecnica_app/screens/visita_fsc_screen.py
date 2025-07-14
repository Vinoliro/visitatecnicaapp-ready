import os
from datetime import datetime

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup

from database.db_manager import DBManager
from utils.gerador_pdf import gerar_pdf_fsc


class VisitaFSCScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.db = DBManager()
        self.fotos_com_observacoes = []  # lista de dicts {"caminho": ..., "obs": ...}

        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=15)

        # Campos básicos: data, produtor, propriedade, chegada, saída
        campos_basicos_layout = GridLayout(cols=2, spacing=10, size_hint_y=None)
        campos_basicos_layout.bind(minimum_height=campos_basicos_layout.setter('height'))

        self.data_input = TextInput(hint_text="Data (DD/MM/AAAA)", multiline=False, size_hint_y=None, height=40)
        self.produtor_input = TextInput(hint_text="Produtor", multiline=False, size_hint_y=None, height=40)
        self.propriedade_input = TextInput(hint_text="Nome da Fazenda", multiline=False, size_hint_y=None, height=40)
        self.chegada_input = TextInput(hint_text="Hora de Chegada (HH:MM)", multiline=False, size_hint_y=None, height=40)
        self.saida_input = TextInput(hint_text="Hora de Saída (HH:MM)", multiline=False, size_hint_y=None, height=40)

        campos_basicos_layout.add_widget(Label(text="Data:", size_hint_y=None, height=40))
        campos_basicos_layout.add_widget(self.data_input)

        campos_basicos_layout.add_widget(Label(text="Produtor:", size_hint_y=None, height=40))
        campos_basicos_layout.add_widget(self.produtor_input)

        campos_basicos_layout.add_widget(Label(text="Nome da Fazenda:", size_hint_y=None, height=40))
        campos_basicos_layout.add_widget(self.propriedade_input)

        campos_basicos_layout.add_widget(Label(text="Hora de Chegada:", size_hint_y=None, height=40))
        campos_basicos_layout.add_widget(self.chegada_input)

        campos_basicos_layout.add_widget(Label(text="Hora de Saída:", size_hint_y=None, height=40))
        campos_basicos_layout.add_widget(self.saida_input)

        main_layout.add_widget(campos_basicos_layout)

        # Scroll para checklist e fotos
        scroll = ScrollView(size_hint=(1, 1))
        inner_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        inner_layout.bind(minimum_height=inner_layout.setter('height'))

        main_layout.add_widget(scroll)
        scroll.add_widget(inner_layout)

        # Checklist itens
        checklist_itens = [
            "Contenção no armazém de agroquímicos",
            "Contenção no tanque de diesel/óleo/gasolina",
            "Lista de estoque de agroquímicos",
            "Identificação em galões de vinagre/gasolina/ethrel",
            "Devolver embalagens de agroquímicos e guardar comprovante",
            "Água corrente e sabonete próximo ao armazém de agroquímicos",
            "Placas de identificação (diesel, agroquímicos, telefones de emergência)",
            "Limpeza de lixo no seringal/quintal",
            "Descarte de lixo / queima de lixo",
            "Kit de primeiros socorros",
            "E.P.I aplicação/manuseio agroquímicos (macacão, máscara e luva)",
            "E.P.I motosserra (calça anticorte, bota com bico de ferro, óculos, protetor auricular, luva de couro)",
            "E.P.I trator (óculos, protetor auricular)",
            "Treino de primeiros socorros",
            "Treino para aplicação e manuseio de agroquimicos",
            "Planilha de controle financeiro",
            "Erosão",
            "Cadastro trabalhadores no aplicativo",
            "Cadastro vizinhos no aplicativo",
        ]

        self.checkboxes = {}

        inner_layout.add_widget(Label(text="Checklist:", bold=True, size_hint_y=None, height=30))

        for item in checklist_itens:
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            cb = CheckBox(size_hint=(None, None), size=(30, 30))
            box.add_widget(cb)
            box.add_widget(Label(text=item, halign="left", valign="middle"))
            inner_layout.add_widget(box)
            self.checkboxes[item] = cb

        # Campo "Outros" com descrição manual
        outros_box = BoxLayout(orientation='vertical', size_hint_y=None, height=100, padding=(0,10))
        outros_box.add_widget(Label(text="Outros (descreva):"))
        self.outros_textinput = TextInput(multiline=True, size_hint_y=None, height=70)
        outros_box.add_widget(self.outros_textinput)
        inner_layout.add_widget(outros_box)

        # Fotos com observações
        fotos_box = BoxLayout(orientation='vertical', size_hint_y=None, height=200, padding=(0,10))
        fotos_box.add_widget(Label(text="Fotos com observações:"))

        self.fotos_list_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.fotos_list_layout.bind(minimum_height=self.fotos_list_layout.setter('height'))
        fotos_box.add_widget(self.fotos_list_layout)

        btn_add_foto = Button(text="Adicionar Foto", size_hint_y=None, height=40)
        btn_add_foto.bind(on_press=self.abrir_seletor_foto)
        fotos_box.add_widget(btn_add_foto)

        inner_layout.add_widget(fotos_box)

        # Botões salvar e voltar
        botoes_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btn_salvar = Button(text="Salvar Visita FSC")
        btn_salvar.bind(on_press=self.salvar_visita_fsc)
        botoes_box.add_widget(btn_salvar)

        btn_voltar = Button(text="Voltar ao Menu")
        btn_voltar.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        botoes_box.add_widget(btn_voltar)

        main_layout.add_widget(botoes_box)

        self.add_widget(main_layout)

    def abrir_seletor_foto(self, instance):
        chooser = FileChooserIconView()

        def selecionar(chooser, selection, touch=None):
            if selection:
                caminho_foto = selection[0]
                popup.dismiss()
                self.pedir_observacao_foto(caminho_foto)

        chooser.bind(on_submit=selecionar)

        popup = Popup(title="Selecionar Foto", content=chooser, size_hint=(0.9, 0.9))
        popup.open()

    def pedir_observacao_foto(self, caminho_foto):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        label = Label(text="Digite a observação para esta foto:")
        txt_observacao = TextInput(multiline=False, size_hint_y=None, height=40)

        btn_ok = Button(text="OK", size_hint_y=None, height=40)
        btn_cancel = Button(text="Cancelar", size_hint_y=None, height=40)

        layout.add_widget(label)
        layout.add_widget(txt_observacao)
        btn_box = BoxLayout(size_hint_y=None, height=40, spacing=10)
        btn_box.add_widget(btn_ok)
        btn_box.add_widget(btn_cancel)
        layout.add_widget(btn_box)

        popup = Popup(title="Observação da Foto", content=layout, size_hint=(0.7, 0.4))

        def confirmar_observacao(instance):
            obs = txt_observacao.text.strip()
            self.fotos_com_observacoes.append({"caminho": caminho_foto, "observacao": obs})
            self.atualizar_lista_fotos()
            popup.dismiss()

        def cancelar(instance):
            popup.dismiss()

        btn_ok.bind(on_press=confirmar_observacao)
        btn_cancel.bind(on_press=cancelar)

        popup.open()

    def atualizar_lista_fotos(self):
        self.fotos_list_layout.clear_widgets()
        for idx, foto in enumerate(self.fotos_com_observacoes):
            texto = f"{os.path.basename(foto['caminho'])} - Obs: {foto['observacao']}"
            label = Label(text=texto, size_hint_y=None, height=30)
            self.fotos_list_layout.add_widget(label)

    def salvar_visita_fsc(self, instance):
        # Validar campos obrigatórios básicos
        if not self.data_input.text.strip():
            self.mostrar_popup("Erro", "Preencha a data.")
            return
        if not self.produtor_input.text.strip():
            self.mostrar_popup("Erro", "Preencha o nome do produtor.")
            return
        if not self.propriedade_input.text.strip():
            self.mostrar_popup("Erro", "Preencha o nome da fazenda.")
            return

        # Preparar dados do checklist
        checklist = {item: cb.active for item, cb in self.checkboxes.items()}
        outros = self.outros_textinput.text.strip()

        dados = {
            "data": self.data_input.text.strip(),
            "produtor": self.produtor_input.text.strip(),
            "propriedade": self.propriedade_input.text.strip(),
            "chegada": self.chegada_input.text.strip(),
            "saida": self.saida_input.text.strip(),
            "checklist": checklist,
            "outros": outros,
            "fotos": self.fotos_com_observacoes,
        }

        # Obter usuário logado
        usuario_logado = None
        try:
            usuario_logado = self.manager.app.usuario_logado
        except AttributeError:
            pass
        usuario_id = usuario_logado['id'] if usuario_logado else None

        # Salvar no banco de dados - adaptar conforme estrutura que deseja salvar
        self.db.inserir_visita({
            "produtor": dados["produtor"],
            "propriedade": dados["propriedade"],
            "municipio": "",  # opcional
            "tecnico": "",  # opcional
            "data": datetime.strptime(dados["data"], "%d/%m/%Y").strftime("%Y-%m-%d"),
            "chegada": dados["chegada"],
            "saida": dados["saida"],
            "divisao_tarefa": 0,
            "borracha_chao": 0,
            "estimulo_intervalo": "",
            "estimulo_conc": "",
            "manutencao": {},
            "foto_path": None,
            "latitude": None,
            "longitude": None
        }, usuario_id=usuario_id)

        # Criar pasta relatorios se não existir
        pasta_relatorios = os.path.join(os.path.dirname(__file__), "..", "relatorios")
        os.makedirs(pasta_relatorios, exist_ok=True)

        nome_arquivo = f"visita_fsc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        caminho_pdf = os.path.join(pasta_relatorios, nome_arquivo)

        # Gerar PDF
        gerar_pdf_fsc(dados, caminho_pdf)

        self.mostrar_popup("Sucesso", "Visita FSC salva e PDF gerado com sucesso.")

        # Limpar campos para próxima entrada (se quiser)
        self.limpar_campos()

        # Voltar para o menu principal
        self.manager.current = "menu"

    def limpar_campos(self):
        self.data_input.text = ""
        self.produtor_input.text = ""
        self.propriedade_input.text = ""
        self.chegada_input.text = ""
        self.saida_input.text = ""
        for cb in self.checkboxes.values():
            cb.active = False
        self.outros_textinput.text = ""
        self.fotos_com_observacoes = []
        self.atualizar_lista_fotos()

    def mostrar_popup(self, titulo, mensagem):
        popup = Popup(title=titulo,
                      content=Label(text=mensagem),
                      size_hint=(0.6, 0.4))
        popup.open()
