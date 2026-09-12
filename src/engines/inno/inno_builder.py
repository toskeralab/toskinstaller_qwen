"""
TOSKINSTALLER - Inno Setup Builder
Construtor de scripts e compilador Inno Setup

Copyright (c) 2024 ToskeraLAB ART/TECH House
Licensed under MIT License
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional, List
import tempfile
import os

from src.models.package_config import PackageConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)


class InnoBuilder:
    """
    Construtor de instaladores usando Inno Setup.
    
    Responsabilidades:
    - Gerar script .iss a partir do template
    - Localizar compilador iscc.exe
    - Executar compilação
    - Retornar caminho do instalador gerado
    """
    
    # Caminhos comuns do Inno Setup
    INNO_PATHS = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe",
    ]
    
    def __init__(self, config: PackageConfig):
        """
        Inicializa o builder com configuração.
        
        Args:
            config: Configuração do pacote
        """
        self.config = config
        self.iscc_path: Optional[Path] = None
        
    def find_compiler(self) -> Optional[Path]:
        """
        Localiza o compilador iscc.exe no sistema.
        
        Returns:
            Caminho do compilador ou None se não encontrado
        """
        # Tentar caminhos conhecidos
        for path in self.INNO_PATHS:
            if Path(path).exists():
                self.iscc_path = Path(path)
                logger.info(f"Inno Setup encontrado: {self.iscc_path}")
                return self.iscc_path
        
        # Tentar via PATH
        iscc = shutil.which("ISCC.exe")
        if iscc:
            self.iscc_path = Path(iscc)
            logger.info(f"Inno Setup encontrado no PATH: {self.iscc_path}")
            return self.iscc_path
        
        logger.warning("Inno Setup não encontrado no sistema")
        return None
    
    def generate_script(self, source_exe: Path, temp_dir: Path) -> Path:
        """
        Gera script .iss a partir do template.
        
        Args:
            source_exe: Executável fonte
            temp_dir: Pasta temporária
            
        Returns:
            Caminho do script .iss gerado
        """
        iss_path = temp_dir / "installer.iss"
        
        # Preparar variáveis do template
        app_name = self.config.app_name
        app_version = self.config.app_version or "1.0.0"
        app_publisher = self.config.publisher or "Unknown"
        app_url = self.config.publisher_url or ""
        
        output_dir = temp_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Configurações de atalhos
        create_desktop = self.config.create_desktop_shortcut
        create_startmenu = self.config.create_startmenu_shortcut
        
        # Tema e cores
        theme = self.config.theme
        primary_color = self.config.primary_color
        secondary_color = self.config.secondary_color
        
        # Apps parceiros
        partner_apps = self.config.partner_apps or []
        
        # Ler template
        template_path = Path(__file__).parent.parent.parent / "templates" / "inno" / "default.iss"
        
        if template_path.exists():
            template_content = template_path.read_text(encoding='utf-8')
        else:
            # Template embutido como fallback
            template_content = self._get_embedded_template()
        
        # Substituir variáveis
        script_content = template_content.format(
            app_name=app_name,
            app_version=app_version,
            app_publisher=app_publisher,
            app_url=app_url,
            app_exe=source_exe.name,
            output_dir=str(output_dir),
            create_desktop="yes" if create_desktop else "no",
            create_startmenu="yes" if create_startmenu else "no",
            primary_color=primary_color,
            secondary_color=secondary_color,
            partners_section=self._generate_partners_section(partner_apps, temp_dir),
            license_text=self._load_license_text()
        )
        
        # Escrever script
        iss_path.write_text(script_content, encoding='utf-8')
        logger.info(f"Script Inno gerado: {iss_path}")
        
        return iss_path
    
    def _generate_partners_section(self, partner_apps: List, temp_dir: Path) -> str:
        """Gera seção de instalação de apps parceiros"""
        if not partner_apps:
            return "; Sem apps parceiros configurados"
        
        lines = ["; Apps Parceiros"]
        
        for i, partner in enumerate(partner_apps):
            partner_path = Path(partner.path).name
            install_order = partner.install_order or 0
            
            lines.append(f"[Files]")
            lines.append(f'Source: "{temp_dir}\\partners\\{partner_path}"; DestDir: "{{tmp}}\\partners"; Flags: dontcopy')
            
            lines.append(f"[Icons]")
            if partner.install_after:
                lines.append(f"; Instalar após app principal")
            
        return "\n".join(lines)
    
    def _load_license_text(self) -> str:
        """Carrega texto da licença"""
        if self.config.license_file and Path(self.config.license_file).exists():
            try:
                content = Path(self.config.license_file).read_text(encoding='utf-8')
                # Escapar caracteres especiais para Inno
                content = content.replace("{", "{{").replace("}", "}}")
                return content
            except Exception as e:
                logger.warning(f"Erro ao ler licença: {e}")
        
        return "Licença não fornecida."
    
    def build(self, source_exe: Path, temp_dir: Path) -> Optional[Path]:
        """
        Compila instalador Inno Setup.
        
        Args:
            source_exe: Executável fonte
            temp_dir: Pasta temporária
            
        Returns:
            Caminho do instalador gerado ou None
        """
        logger.info("Iniciando build Inno Setup...")
        
        # Localizar compilador
        compiler = self.find_compiler()
        if not compiler:
            raise FileNotFoundError(
                "Inno Setup não encontrado. "
                "Instale em https://jrsoftware.org/isdl.php ou permita download automático."
            )
        
        # Gerar script
        iss_script = self.generate_script(source_exe, temp_dir)
        
        # Comando de compilação
        output_dir = temp_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        cmd = [
            str(compiler),
            "/Q",  # Modo quiet
            f"/O{output_dir}",  # Output directory
            f"/F{self.config.app_name}_Setup_{self.config.app_version or '1.0.0'}",  # Output filename
            str(iss_script)
        ]
        
        logger.info(f"Executando: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutos timeout
                check=False
            )
            
            if result.returncode == 0:
                # Encontrar arquivo gerado
                installer_pattern = f"{self.config.app_name}_Setup_*.exe"
                installers = list(output_dir.glob(installer_pattern))
                
                if installers:
                    installer_path = installers[0]
                    logger.info(f"Instalador gerado: {installer_path}")
                    return installer_path
                else:
                    logger.error("Nenhum instalador encontrado na saída")
                    return None
            else:
                logger.error(f"Erro na compilação Inno:\n{result.stderr}")
                raise RuntimeError(f"Inno Setup falhou: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout na compilação Inno Setup")
            raise RuntimeError("Compilação Inno Setup excedeu tempo limite")
        except Exception as e:
            logger.error(f"Erro na compilação: {e}")
            raise
    
    def _get_embedded_template(self) -> str:
        """Retorna template embutido caso arquivo externo não exista"""
        return """
#define MyAppName "{app_name}"
#define MyAppVersion "{app_version}"
#define MyAppPublisher "{app_publisher}"
#define MyAppURL "{app_url}"
#define MyAppExeName "{app_exe}"

[Setup]
AppId={#MyAppName}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={{pf}}\\{{#MyAppName}}
DefaultGroupName={{#MyAppName}}
AllowNoIcons=yes
LicenseFile=
OutputDir={output_dir}
OutputBaseFilename={#MyAppName}_Setup_{#MyAppVersion}
SetupIconFile=
UninstallDisplayIcon={{app}}\\{{#MyAppExeName}}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
WizardImageFile=
WizardSmallImageFile=

[Languages]
Name: "english"; MessagesFile: "compiler:Default.ism"
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\\BrazilianPortuguese.ism"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: {create_desktop}
Name: "quicklaunchicon"; Description: "{{cm:CreateQuickLaunchIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "{{app}}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{autodesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon
Name: "{{userappdata}}\\Microsoft\\Internet Explorer\\Quick Launch\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: quicklaunchicon

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

{partners_section}

[Code]
procedure InitializeWizard;
begin
  WizardForm.LicenseLabel.Caption:='{license_text}';
end;
""".strip()
