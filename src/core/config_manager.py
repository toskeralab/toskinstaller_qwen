"""
TOSKINSTALLER - Gerenciador de Configurações

Gerencia configurações do usuário em formato JSON.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from src.core.logger import get_logger

logger = get_logger(__name__)


class OutputFormat(Enum):
    """Formatos de saída suportados."""
    EXE = "exe"
    MSI = "msi"
    PORTABLE = "portable"


class InstallMode(Enum):
    """Modos de instalação."""
    INSTALLED = "installed"
    PORTABLE = "portable"


class AnimationStyle(Enum):
    """Estilos de animação de progresso."""
    CIRCLE = "circle"
    BAR = "bar"
    DOTS = "dots"
    PULSE = "pulse"
    TOSKERA = "toskera"


class Theme(Enum):
    """Temas de UI."""
    LIGHT = "light"
    DARK = "dark"
    TOSKERA = "toskera"


@dataclass
class PartnerApp:
    """Aplicativo parceiro para instalação opcional."""
    name: str
    path: str
    install_before: bool = False
    silent_args: str = ""
    required: bool = False
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SigningConfig:
    """Configuração de assinatura digital."""
    enabled: bool = False
    certificate_path: str = ""
    password: str = ""
    timestamp_url: str = "http://timestamp.digicert.com"
    
    def to_dict(self) -> dict:
        return {
            'enabled': self.enabled,
            'certificate_path': self.certificate_path,
            'password': '***' if self.password else '',  # Não salvar senha real
            'timestamp_url': self.timestamp_url,
        }


@dataclass
class PackageConfig:
    """Configuração completa do pacote."""
    # Formatos de saída
    output_formats: list = None
    
    # Instalação
    install_mode: str = InstallMode.INSTALLED.value
    target_folder: str = ""
    create_desktop_shortcut: bool = True
    create_start_menu_shortcut: bool = True
    
    # UI Customization
    theme: str = Theme.DARK.value
    animation_style: str = AnimationStyle.BAR.value
    primary_color: str = "#0078D4"
    secondary_color: str = "#106EBE"
    logo_path: str = ""
    banner_path: str = ""
    license_text: str = ""
    
    # Apps parceiros
    partner_apps: list = None
    
    # Assinatura
    signing: dict = None
    
    # Arquitetura
    architecture: str = "x64"
    
    # Internacionalização
    language: str = "pt-BR"
    
    def __post_init__(self):
        if self.output_formats is None:
            self.output_formats = [OutputFormat.EXE.value]
        if self.partner_apps is None:
            self.partner_apps = []
        if self.signing is None:
            self.signing = SigningConfig().to_dict()
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PackageConfig':
        return cls(**data)


class ConfigManager:
    """
    Gerenciador de configurações do TOSKINSTALLER.
    
    Salva/carrega configurações em JSON.
    """
    
    DEFAULT_CONFIG_FILE = ".toskinstaller/config.json"
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = Path(config_file) if config_file else None
        self.logger = get_logger(__name__)
        self._config: Dict[str, Any] = {}
    
    def load(self, project_path: str) -> PackageConfig:
        """
        Carrega configurações salvas para um projeto.
        
        Args:
            project_path: Caminho do projeto
        
        Returns:
            PackageConfig carregado ou padrão
        """
        config_path = Path(project_path) / self.DEFAULT_CONFIG_FILE
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.logger.info(f"Configuração carregada de: {config_path}")
                return PackageConfig.from_dict(data)
            except Exception as e:
                self.logger.warning(f"Erro ao carregar configuração: {e}")
        
        self.logger.info("Usando configuração padrão")
        return PackageConfig()
    
    def save(self, project_path: str, config: PackageConfig) -> bool:
        """
        Salva configurações para um projeto.
        
        Args:
            project_path: Caminho do projeto
            config: Configuração para salvar
        
        Returns:
            True se salvou com sucesso
        """
        config_dir = Path(project_path) / ".toskinstaller"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        config_path = config_dir / "config.json"
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuração salva em: {config_path}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar configuração: {e}")
            return False
    
    def get_defaults(self) -> PackageConfig:
        """Retorna configuração padrão."""
        return PackageConfig()
    
    def validate(self, config: PackageConfig) -> tuple[bool, list[str]]:
        """
        Valida configuração.
        
        Returns:
            Tuple (valid, errors)
        """
        errors = []
        
        # Validar formatos
        valid_formats = [f.value for f in OutputFormat]
        for fmt in config.output_formats:
            if fmt not in valid_formats:
                errors.append(f"Formato inválido: {fmt}")
        
        # Validar arquitetura
        valid_archs = ["x86", "x64", "arm64"]
        if config.architecture not in valid_archs:
            errors.append(f"Arquitetura inválida: {config.architecture}")
        
        # Validar idioma
        valid_langs = ["pt-BR", "en"]
        if config.language not in valid_langs:
            errors.append(f"Idioma inválido: {config.language}")
        
        # Validar certificado se assinatura habilitada
        if config.signing.get('enabled'):
            cert_path = config.signing.get('certificate_path')
            if cert_path and not Path(cert_path).exists():
                errors.append(f"Certificado não encontrado: {cert_path}")
        
        return len(errors) == 0, errors
