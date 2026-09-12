"""
TOSKINSTALLER - Core Module

Módulo central responsável por:
- Detecção de linguagem de projetos
- Gerenciamento de ferramentas de compilação
- Empacotamento final
- Instalação automática de ferramentas externas
"""

from src.core.detector import ProjectDetector
from src.core.compiler_manager import CompilerManager
from src.core.packager import Packager
from src.core.config_manager import ConfigManager
from src.core.logger import setup_logger
from src.core.tool_installer import ToolInstaller

__all__ = [
    'ProjectDetector',
    'CompilerManager',
    'Packager',
    'ConfigManager',
    'setup_logger',
    'ToolInstaller',
]