from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from screens.login_screen import LoginScreen
from screens.cadastro_screen import CadastroScreen
from screens.menu_screen import MenuScreen
from screens.nova_visita_screen import NovaVisitaScreen
from screens.historico_screen import HistoricoScreen
from screens.detalhes_visita_screen import DetalhesVisitaScreen
from screens.estatisticas_screen import EstatisticasScreen
from screens.selecao_visita_screen import SelecaoVisitaScreen
from screens.visita_fsc_screen import VisitaFSCScreen  # NOVO

class VisitApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.usuario_logado = None

        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(CadastroScreen(name='cadastro'))
        self.sm.add_widget(MenuScreen(name='menu'))
        self.sm.add_widget(SelecaoVisitaScreen(name='selecao_visita'))  # NOVO
        self.sm.add_widget(NovaVisitaScreen(name='nova_visita'))
        self.sm.add_widget(VisitaFSCScreen(name='visita_fsc'))          # NOVO
        self.sm.add_widget(HistoricoScreen(name='historico'))
        self.sm.add_widget(DetalhesVisitaScreen(name='detalhes_visita'))
        self.sm.add_widget(EstatisticasScreen(name='estatisticas'))

        return self.sm

if __name__ == '__main__':
    VisitApp().run()
