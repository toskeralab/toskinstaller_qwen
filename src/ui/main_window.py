"""
TOSKINSTALLER - Janela Principal
Interface principal do aplicativo com navegação por wizard
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QLabel, QPushButton, QFrame,
    QProgressBar, QStatusBar
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QFont, QIcon

from .wizard.wizard_controller import WizardController
from src.core.logger import get_logger

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """Janela principal do TOSKINSTALLER"""
    
    # Sinais
    project_loaded = Signal(str)  # caminho do projeto
    build_started = Signal()
    build_completed = Signal(str)  # caminho do pacote gerado
    build_failed = Signal(str)  # mensagem de erro
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("TOSKINSTALLER - ToskeraLAB")
        self.setMinimumSize(900, 700)
        self.resize(1000, 750)
        
        # Controller do wizard
        self.wizard_controller = None
        
        self._setup_ui()
        self._setup_statusbar()
        
        logger.info("MainWindow inicializada")
        
    def _setup_ui(self):
        """Configura a interface principal"""
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal vertical
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setFixedHeight(80)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 15, 30, 15)
        
        # Logo e título
        title_label = QLabel("TOSKINSTALLER")
        title_label.setObjectName("title")
        title_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        
        subtitle_label = QLabel("by ToskeraLAB ART/TECH House")
        subtitle_label.setObjectName("subtitle")
        subtitle_label.setFont(QFont("Segoe UI", 12))
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(subtitle_label)
        
        main_layout.addWidget(header_frame)
        
        # Área do wizard (stacked widget)
        self.wizard_stack = QStackedWidget()
        self.wizard_stack.setObjectName("wizardContainer")
        main_layout.addWidget(self.wizard_stack, 1)
        
        # Footer com botões de navegação
        footer_frame = QFrame()
        footer_frame.setObjectName("footerFrame")
        footer_frame.setFixedHeight(70)
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(30, 15, 30, 15)
        footer_layout.setSpacing(15)
        
        # Botão Voltar
        self.back_button = QPushButton("← Voltar")
        self.back_button.setObjectName("backButton")
        self.back_button.setFixedSize(120, 40)
        self.back_button.clicked.connect(self._on_back_clicked)
        
        footer_layout.addWidget(self.back_button)
        footer_layout.addStretch()
        
        # Indicador de etapa
        self.step_label = QLabel("Etapa 1 de 8")
        self.step_label.setFont(QFont("Segoe UI", 11))
        self.step_label.setAlignment(Qt.AlignCenter)
        footer_layout.addWidget(self.step_label)
        
        footer_layout.addStretch()
        
        # Botão Avançar/Concluir
        self.next_button = QPushButton("Avançar →")
        self.next_button.setObjectName("nextButton")
        self.next_button.setFixedSize(120, 40)
        self.next_button.clicked.connect(self._on_next_clicked)
        
        footer_layout.addWidget(self.next_button)
        
        main_layout.addWidget(footer_frame)
        
        # Inicializar controller do wizard
        self.wizard_controller = WizardController(self.wizard_stack)
        self.wizard_controller.current_step_changed.connect(self._update_step_indicator)
        self.wizard_controller.validation_changed.connect(self._update_navigation_buttons)
        
        # Atualizar estado inicial dos botões
        self._update_navigation_buttons()
        
    def _setup_statusbar(self):
        """Configura a barra de status"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Pronto para iniciar")
        
    @Slot()
    def _on_back_clicked(self):
        """Handler do botão Voltar"""
        if self.wizard_controller:
            self.wizard_controller.previous_step()
            
    @Slot()
    def _on_next_clicked(self):
        """Handler do botão Avançar"""
        if self.wizard_controller:
            if self.wizard_controller.is_last_step():
                # Último passo - iniciar processo de build
                self._start_build_process()
            else:
                self.wizard_controller.next_step()
                
    def _update_step_indicator(self, step_index: int, total_steps: int):
        """Atualiza o indicador de etapa"""
        self.step_label.setText(f"Etapa {step_index + 1} de {total_steps}")
        
        # Atualizar estado do botão Voltar
        self.back_button.setEnabled(step_index > 0)
        
        # Atualizar texto do botão Avançar
        if self.wizard_controller and self.wizard_controller.is_last_step():
            self.next_button.setText("Gerar Pacote")
        else:
            self.next_button.setText("Avançar →")
            
    def _update_navigation_buttons(self):
        """Atualiza o estado dos botões de navegação baseado na validação"""
        if not self.wizard_controller:
            return
            
        is_valid = self.wizard_controller.is_current_step_valid()
        self.next_button.setEnabled(is_valid)
        
        # Sempre habilitar botão Voltar exceto na primeira página
        current_step = self.wizard_controller.get_current_step_index()
        self.back_button.setEnabled(current_step > 0)
        
    def _start_build_process(self):
        """Inicia o processo de build do pacote"""
        logger.info("Iniciando processo de build")
        self.statusbar.showMessage("Processando... aguarde")
        
        # Desabilitar botões durante o build
        self.back_button.setEnabled(False)
        self.next_button.setEnabled(False)
        
        try:
            # Obter configuração do wizard
            config = self.wizard_controller.get_config()
            
            # TODO: Implementar chamada ao packager
            # Por enquanto, simular sucesso
            self.statusbar.showMessage("Build concluído com sucesso!")
            self.build_completed.emit("")
            
        except Exception as e:
            logger.error(f"Erro no build: {e}")
            self.statusbar.showMessage(f"Erro: {str(e)}")
            self.build_failed.emit(str(e))
        finally:
            # Reabilitar botões
            self.back_button.setEnabled(True)
            if self.wizard_controller:
                self.next_button.setEnabled(
                    self.wizard_controller.is_current_step_valid()
                )
                
    def get_wizard_controller(self) -> WizardController:
        """Retorna o controller do wizard"""
        return self.wizard_controller
        
    def closeEvent(self, event):
        """Handler do evento de fechamento"""
        logger.info("Fechando aplicação...")
        event.accept()
