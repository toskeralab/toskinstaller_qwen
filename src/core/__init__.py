"""
TOSKINSTALLER - Core Module

Módulo central responsável por:
- Detecção de linguagem de projetos
- Gerenciamento de ferramentas de compilação
- Empacotamento final
- Instalação automática de ferramentas externas
"""

from .detector import ProjectDetector
from .compiler_manager import CompilerManager
from .packager import Packager
from .config_manager import ConfigManager
from .logger import setup_logger
from .tool_installer import ToolInstaller

__all__ = [
    'ProjectDetector',
    'CompilerManager',
    'Packager',
    'ConfigManager',
    'setup_logger',
    'ToolInstaller',
]