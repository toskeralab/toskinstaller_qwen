"""
Widget de Animação de Progresso
Suporta 5 templates pré-definidos com customização de cores
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from PySide6.QtQuick import QQuickView, QQuickWidget
from PySide6.QtCore import Qt, QUrl, Property, Signal, Slot
from PySide6.QtGui import QColor
import os


class ProgressAnimationWidget(QWidget):
    """Widget que exibe animações de progresso com 5 templates diferentes"""
    
    progress_changed = Signal(float)  # 0.0 a 1.0
    
    # Templates disponíveis
    TEMPLATES = {
        'circle': 'progress_circle.qml',
        'bar': 'progress_bar.qml',
        'dots': 'progress_dots.qml',
        'pulse': 'progress_pulse.qml',
        'toskera': 'progress_toskera.qml'
    }
    
    def __init__(self, parent=None, template='toskera'):
        super().__init__(parent)
        self._progress = 0.0
        self._template = template
        self._primary_color = QColor('#3498db')
        self._secondary_color = QColor('#2ecc71')
        
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Stack widget para múltiplos templates
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        # Carregar todos os templates
        self.views = {}
        base_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'animations')
        
        for name, qml_file in self.TEMPLATES.items():
            qml_path = os.path.join(base_path, qml_file)
            
            if not os.path.exists(qml_path):
                # Fallback para widget simples se QML não existir
                from PySide6.QtWidgets import QLabel
                fallback = QLabel(f"Template: {name}")
                fallback.setAlignment(Qt.AlignCenter)
                self.stack.addWidget(fallback)
                self.views[name] = None
                continue
            
            # Criar QQuickWidget para o QML
            quick_widget = QQuickWidget(QUrl.fromLocalFile(qml_path))
            quick_widget.setMinimumSize(300, 200)
            quick_widget.setMaximumSize(500, 300)
            quick_widget.setSizePolicy(
                quick_widget.sizePolicy().horizontalPolicy(),
                quick_widget.sizePolicy().verticalPolicy()
            )
            
            self.stack.addWidget(quick_widget)
            self.views[name] = quick_widget
            
            # Conectar sinal de resize
            quick_widget.resizeEvent = lambda e, qw=quick_widget: self._on_resize(qw, e)
        
        # Selecionar template inicial
        self.set_template(self._template)
        
    def _on_resize(self, quick_widget, event):
        """Handle resize events para manter aspect ratio"""
        pass
        
    def set_template(self, template_name: str):
        """Muda o template de animação"""
        if template_name in self.TEMPLATES:
            self._template = template_name
            index = list(self.TEMPLATES.keys()).index(template_name)
            self.stack.setCurrentIndex(index)
            
            # Atualizar propriedades no QML
            self._update_qml_properties()
            
    def set_progress(self, value: float):
        """Atualiza o progresso (0.0 a 1.0)"""
        self._progress = max(0.0, min(1.0, value))
        self._update_qml_properties()
        self.progress_changed.emit(self._progress)
        
    def _update_qml_properties(self):
        """Atualiza propriedades nos widgets QML"""
        current_view = self.stack.currentWidget()
        if current_view and isinstance(current_view, QQuickWidget):
            root_obj = current_view.rootObject()
            if root_obj:
                root_obj.setProperty('progressValue', self._progress)
                
                # Atualizar cores se as propriedades existirem
                if root_obj.property('primaryColor'):
                    root_obj.setProperty('primaryColor', self._primary_color)
                if root_obj.property('dotColor'):
                    root_obj.setProperty('dotColor', self._primary_color)
                if root_obj.property('pulseColor'):
                    root_obj.setProperty('pulseColor', self._primary_color)
                    
    def set_colors(self, primary: QColor, secondary: QColor = None):
        """Define as cores da animação"""
        self._primary_color = primary
        if secondary:
            self._secondary_color = secondary
        self._update_qml_properties()
        
    def get_available_templates(self) -> list:
        """Retorna lista de templates disponíveis"""
        return list(self.TEMPLATES.keys())
        
    @Slot()
    def reset(self):
        """Reseta o progresso para 0"""
        self.set_progress(0.0)
        
    @Slot()
    def complete(self):
        """Completa a animação (progresso = 1.0)"""
        self.set_progress(1.0)
