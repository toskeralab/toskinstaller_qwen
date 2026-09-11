"""
TOSKINSTALLER - Package Configuration Model
Modelo para configuração completa do pacote

Copyright (c) 2024 ToskeraLAB ART/TECH House
Licensed under MIT License
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
from pathlib import Path
from datetime import datetime


class OutputFormat(Enum):
    """Formatos de saída suportados"""
    EXE_INSTALLER = "exe"
    MSI_INSTALLER = "msi"
    PORTABLE = "portable"


class ThemeOption(Enum):
    """Temas de UI disponíveis"""
    LIGHT = "light"
    DARK = "dark"
    TOSKERA = "toskera"
    CUSTOM = "custom"


class AnimationOption(Enum):
    """Animações de progresso disponíveis"""
    CIRCLE = "circle"
    BAR = "bar"
    DOTS = "dots"
    PULSE = "pulse"
    TOSKERA = "toskera"


@dataclass
class PartnerApp:
    """Modelo para aplicativo parceiro"""
    name: str
    path: str
    install_order: int = 0
    install_after: bool = True
    silent_install: bool = True
    install_condition: str = ""
    required: bool = False
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'path': self.path,
            'install_order': self.install_order,
            'install_after': self.install_after,
            'silent_install': self.silent_install,
            'required': self.required
        }


@dataclass
class SigningConfig:
    """Configuração de assinatura digital"""
    enabled: bool = False
    certificate_path: str = ""
    password: str = ""
    timestamp_url: str = "http://timestamp.digicert.com"
    subject_name: str = ""
    algorithm: str = "SHA256"
    
    @property
    def is_valid(self) -> bool:
        return self.enabled and bool(self.certificate_path)


@dataclass
class PackageConfig:
    """
    Configuração completa do pacote a ser gerado.
    
    Atributos:
        app_name: Nome do aplicativo
        app_version: Versão do aplicativo
        publisher: Nome do publicador
        publisher_url: URL do publicador
        
        output_formats: Lista de formatos a gerar
        architecture: Arquitetura alvo (x64, x86, arm64)
        
        install_dir: Diretório de instalação padrão
        create_desktop_shortcut: Criar atalho na área de trabalho
        create_startmenu_shortcut: Criar atalho no Menu Iniciar
        
        theme: Tema da UI
        primary_color: Cor primária (hex)
        secondary_color: Cor secundária (hex)
        animation: Tipo de animação de progresso
        
        logo_path: Caminho para logo
        banner_welcome: Banner de boas-vindas
        banner_complete: Banner de conclusão
        license_file: Arquivo de licença
        
        partner_apps: Lista de apps parceiros
        signing_config: Configuração de assinatura
        
        additional_files: Arquivos adicionais para incluir
        keep_temp_files: Manter arquivos temporários após build
        
        language: Idioma (pt-BR, en)
        created_at: Data de criação da config
    """
    
    # Informações do aplicativo
    app_name: str = "MyApplication"
    app_version: str = "1.0.0"
    publisher: str = ""
    publisher_url: str = ""
    description: str = ""
    
    # Formatos de saída
    output_formats: List[OutputFormat] = field(default_factory=lambda: [OutputFormat.EXE_INSTALLER])
    architecture: str = "x64"
    
    # Opções de instalação
    install_dir: str = ""
    create_desktop_shortcut: bool = True
    create_startmenu_shortcut: bool = True
    allow_user_choice_dir: bool = True
    
    # Customização de UI
    theme: ThemeOption = ThemeOption.TOSKERA
    primary_color: str = "#1E90FF"
    secondary_color: str = "#00CED1"
    animation: AnimationOption = AnimationOption.CIRCLE
    
    # Assets
    logo_path: Optional[str] = None
    banner_welcome: Optional[str] = None
    banner_complete: Optional[str] = None
    license_file: Optional[str] = None
    
    # Apps parceiros
    partner_apps: List[PartnerApp] = field(default_factory=list)
    
    # Assinatura digital
    signing_config: Optional[SigningConfig] = None
    
    # Arquivos adicionais
    additional_files: List[str] = field(default_factory=list)
    
    # Comportamento
    keep_temp_files: bool = False
    verbose: bool = True
    
    # Internacionalização
    language: str = "pt-BR"
    
    # Metadados
    created_at: datetime = field(default_factory=datetime.now)
    config_file: Optional[str] = None
    
    @property
    def enable_signing(self) -> bool:
        """Verifica se assinatura está habilitada"""
        return self.signing_config is not None and self.signing_config.is_valid
    
    def add_format(self, fmt: OutputFormat):
        """Adiciona formato de saída"""
        if fmt not in self.output_formats:
            self.output_formats.append(fmt)
    
    def remove_format(self, fmt: OutputFormat):
        """Remove formato de saída"""
        if fmt in self.output_formats:
            self.output_formats.remove(fmt)
    
    def add_partner_app(self, partner: PartnerApp):
        """Adiciona app parceiro"""
        self.partner_apps.append(partner)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário JSON-serializable"""
        return {
            'app_name': self.app_name,
            'app_version': self.app_version,
            'publisher': self.publisher,
            'publisher_url': self.publisher_url,
            'description': self.description,
            'output_formats': [f.value for f in self.output_formats],
            'architecture': self.architecture,
            'install_dir': self.install_dir,
            'create_desktop_shortcut': self.create_desktop_shortcut,
            'create_startmenu_shortcut': self.create_startmenu_shortcut,
            'allow_user_choice_dir': self.allow_user_choice_dir,
            'theme': self.theme.value,
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color,
            'animation': self.animation.value,
            'logo_path': self.logo_path,
            'banner_welcome': self.banner_welcome,
            'banner_complete': self.banner_complete,
            'license_file': self.license_file,
            'partner_apps': [p.to_dict() for p in self.partner_apps],
            'signing_config': self.signing_config.__dict__ if self.signing_config else None,
            'additional_files': self.additional_files,
            'keep_temp_files': self.keep_temp_files,
            'verbose': self.verbose,
            'language': self.language,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PackageConfig':
        """Cria instância a partir de dicionário"""
        # Converter enums
        output_formats = [OutputFormat(f) for f in data.get('output_formats', ['exe'])]
        theme = ThemeOption(data.get('theme', 'toskera'))
        animation = AnimationOption(data.get('animation', 'circle'))
        
        # Converter signing config
        signing_data = data.get('signing_config')
        signing_config = SigningConfig(**signing_data) if signing_data else None
        
        # Converter partner apps
        partner_apps = [PartnerApp(**p) for p in data.get('partner_apps', [])]
        
        config = cls(
            app_name=data.get('app_name', 'MyApplication'),
            app_version=data.get('app_version', '1.0.0'),
            publisher=data.get('publisher', ''),
            publisher_url=data.get('publisher_url', ''),
            description=data.get('description', ''),
            output_formats=output_formats,
            architecture=data.get('architecture', 'x64'),
            install_dir=data.get('install_dir', ''),
            create_desktop_shortcut=data.get('create_desktop_shortcut', True),
            create_startmenu_shortcut=data.get('create_startmenu_shortcut', True),
            allow_user_choice_dir=data.get('allow_user_choice_dir', True),
            theme=theme,
            primary_color=data.get('primary_color', '#1E90FF'),
            secondary_color=data.get('secondary_color', '#00CED1'),
            animation=animation,
            logo_path=data.get('logo_path'),
            banner_welcome=data.get('banner_welcome'),
            banner_complete=data.get('banner_complete'),
            license_file=data.get('license_file'),
            partner_apps=partner_apps,
            signing_config=signing_config,
            additional_files=data.get('additional_files', []),
            keep_temp_files=data.get('keep_temp_files', False),
            verbose=data.get('verbose', True),
            language=data.get('language', 'pt-BR')
        )
        
        return config
    
    def save_json(self, path: str):
        """Salva configuração em arquivo JSON"""
        import json
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        self.config_file = path
    
    @classmethod
    def load_json(cls, path: str) -> 'PackageConfig':
        """Carrega configuração de arquivo JSON"""
        import json
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        config = cls.from_dict(data)
        config.config_file = path
        return config
