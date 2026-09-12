"""
TOSKINSTALLER - WiX Toolset Builder
Construtor de scripts e compilador WiX para MSI

Copyright (c) 2024 ToskeraLAB ART/TECH House
Licensed under MIT License
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional, List
import uuid
import os

from src.models.package_config import PackageConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)


class WixBuilder:
    """
    Construtor de instaladores MSI usando WiX Toolset.
    
    Responsabilidades:
    - Gerar script .wxs a partir do template
    - Localizar ferramentas WiX (candle, light)
    - Executar compilação e link
    - Retornar caminho do MSI gerado
    """
    
    # Caminhos comuns do WiX Toolset
    WIX_PATHS = [
        r"C:\Program Files\WiX Toolset v5\bin",
        r"C:\Program Files (x86)\WiX Toolset v5\bin",
        r"C:\Program Files\WiX Toolset v3.14\bin",
        r"C:\Program Files (x86)\WiX Toolset v3.14\bin",
    ]
    
    def __init__(self, config: PackageConfig):
        """
        Inicializa o builder com configuração.
        
        Args:
            config: Configuração do pacote
        """
        self.config = config
        self.wix_path: Optional[Path] = None
        self.candle_path: Optional[Path] = None
        self.light_path: Optional[Path] = None
        
    def find_tools(self) -> bool:
        """
        Localiza ferramentas WiX no sistema.
        
        Returns:
            True se encontrado, False caso contrário
        """
        # Tentar caminhos conhecidos
        for path in self.WIX_PATHS:
            wix_dir = Path(path)
            if wix_dir.exists():
                candle = wix_dir / "candle.exe"
                light = wix_dir / "light.exe"
                
                if candle.exists() and light.exists():
                    self.wix_path = wix_dir
                    self.candle_path = candle
                    self.light_path = light
                    logger.info(f"WiX Toolset encontrado: {self.wix_path}")
                    return True
        
        # Tentar via PATH
        candle = shutil.which("candle.exe")
        light = shutil.which("light.exe")
        
        if candle and light:
            self.candle_path = Path(candle)
            self.light_path = Path(light)
            self.wix_path = self.candle_path.parent
            logger.info(f"WiX Toolset encontrado no PATH")
            return True
        
        logger.warning("WiX Toolset não encontrado no sistema")
        return False
    
    def generate_product_id(self) -> str:
        """Gera UUID único para o produto"""
        return str(uuid.uuid4()).upper()
    
    def generate_script(self, source_exe: Path, temp_dir: Path) -> Path:
        """
        Gera script .wxs a partir do template.
        
        Args:
            source_exe: Executável fonte
            temp_dir: Pasta temporária
            
        Returns:
            Caminho do script .wxs gerado
        """
        wxs_path = temp_dir / "installer.wxs"
        
        # Preparar variáveis
        app_name = self.config.app_name
        app_version = self.config.app_version or "1.0.0"
        manufacturer = self.config.publisher or "Unknown"
        product_id = self.generate_product_id()
        
        # UpgradeCode consistente para mesmo app
        upgrade_code = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{app_name}_{manufacturer}")).upper()
        
        output_dir = temp_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Configurações de atalhos
        create_desktop = self.config.create_desktop_shortcut
        create_startmenu = self.config.create_startmenu_shortcut
        
        # Apps parceiros
        partner_apps = self.config.partner_apps or []
        
        # Ler template
        template_path = Path(__file__).parent.parent.parent / "templates" / "wix" / "default.wxs"
        
        if template_path.exists():
            template_content = template_path.read_text(encoding='utf-8')
        else:
            template_content = self._get_embedded_template()
        
        # Substituir variáveis
        script_content = template_content.format(
            product_id=product_id,
            upgrade_code=upgrade_code,
            app_name=app_name,
            app_version=app_version,
            manufacturer=manufacturer,
            app_exe=source_exe.name,
            create_desktop="yes" if create_desktop else "no",
            create_startmenu="yes" if create_startmenu else "no",
            partners_component=self._generate_partners_component(partner_apps),
            license_rtf=self._convert_license_to_rtf()
        )
        
        # Escrever script
        wxs_path.write_text(script_content, encoding='utf-8')
        logger.info(f"Script WiX gerado: {wxs_path}")
        
        return wxs_path
    
    def _generate_partners_component(self, partner_apps: List) -> str:
        """Gera componente de apps parceiros"""
        if not partner_apps:
            return "<!-- Sem apps parceiros -->"
        
        components = ["<!-- Apps Parceiros -->"]
        
        for i, partner in enumerate(partner_apps):
            partner_name = Path(partner.path).stem
            partner_exe = Path(partner.path).name
            
            components.append(f"""
<Component Id=\"PartnerApp{i}\" Guid=\"{str(uuid.uuid4()).upper()}\">
    <File Source=\"$(var.PartnersDir)\\{partner_exe}\" KeyPath=\"yes\" />
    <Condition>{partner.install_condition or '1'}</Condition>
</Component>""")
        
        return "\n".join(components)
    
    def _convert_license_to_rtf(self) -> str:
        """Converte licença para formato RTF simples"""
        if self.config.license_file and Path(self.config.license_file).exists():
            try:
                content = Path(self.config.license_file).read_text(encoding='utf-8')
                # RTF básico
                rtf_content = r"{\rtf1\ansi " + content.replace("\n", "\\par ") + "}"
                return rtf_content
            except Exception as e:
                logger.warning(f"Erro ao converter licença: {e}")
        
        return r"{\rtf1\ansi Licença não fornecida.}"
    
    def build(self, source_exe: Path, temp_dir: Path) -> Optional[Path]:
        """
        Compila instalador MSI usando WiX.
        
        Args:
            source_exe: Executável fonte
            temp_dir: Pasta temporária
            
        Returns:
            Caminho do MSI gerado ou None
        """
        logger.info("Iniciando build WiX...")
        
        # Localizar ferramentas
        if not self.find_tools():
            raise FileNotFoundError(
                "WiX Toolset não encontrado. "
                "Instale em https://github.com/wixtoolset/wix3/releases ou permita download automático."
            )
        
        # Gerar script
        wxs_script = self.generate_script(source_exe, temp_dir)
        
        # Diretórios de trabalho
        obj_dir = temp_dir / "obj"
        obj_dir.mkdir(exist_ok=True)
        output_dir = temp_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        msi_filename = f"{self.config.app_name}_Setup_{self.config.app_version or '1.0.0'}.msi"
        
        # Passo 1: Candle (compilar .wxs para .wixobj)
        candle_cmd = [
            str(self.candle_path),
            "-out", str(obj_dir / "installer.wixobj"),
            f"-DappDir={temp_dir}\\app",
            f"-DPartnersDir={temp_dir}\\partners",
            str(wxs_script)
        ]
        
        logger.info(f"Candle: {' '.join(candle_cmd)}")
        
        try:
            result = subprocess.run(
                candle_cmd,
                capture_output=True,
                text=True,
                timeout=120,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"Erro no Candle:\n{result.stderr}")
                raise RuntimeError(f"Candle falhou: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise RuntimeError("Candle excedeu tempo limite")
        
        # Passo 2: Light (linkar .wixobj para .msi)
        light_cmd = [
            str(self.light_path),
            "-out", str(output_dir / msi_filename),
            "-spdb",  # Suprimir pdb
            "-sice:ICE69",  # Suprimir warning de referência entre componentes
            str(obj_dir / "installer.wixobj")
        ]
        
        logger.info(f"Light: {' '.join(light_cmd)}")
        
        try:
            result = subprocess.run(
                light_cmd,
                capture_output=True,
                text=True,
                timeout=180,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"Erro no Light:\n{result.stderr}")
                raise RuntimeError(f"Light falhou: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise RuntimeError("Light excedeu tempo limite")
        
        # Verificar saída
        msi_path = output_dir / msi_filename
        if msi_path.exists():
            logger.info(f"MSI gerado: {msi_path}")
            return msi_path
        else:
            logger.error("MSI não gerado")
            return None
    
    def _get_embedded_template(self) -> str:
        """Retorna template embutido"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
    <Product 
        Id="{product_id}"
        Name="{app_name}"
        Language="1033"
        Version="{app_version}"
        Manufacturer="{manufacturer}"
        UpgradeCode="{upgrade_code}">
        
        <Package 
            InstallerVersion="500" 
            Compressed="yes" 
            InstallScope="perMachine"
            Description="Instalador de {app_name}" />
        
        <MajorUpgrade 
            DowngradeErrorMessage="Uma versão mais recente já está instalada." />
        
        <MediaTemplate EmbedCab="yes" />
        
        <UI>
            <UIRef Id="WixUI_InstallDir" />
            <Property Id="WIXUI_INSTALLDIR" Value="INSTALLDIR" />
        </UI>
        
        <Directory Id="TARGETDIR" Name="SourceDir">
            <Directory Id="ProgramFilesFolder">
                <Directory Id="INSTALLDIR" Name="{app_name}">
                    <Component Id="MainExecutable" Guid="*">
                        <File Source="$(var.appDir)\\{app_exe}" KeyPath="yes" />
                    </Component>
                    
                    {partners_component}
                </Directory>
            </Directory>
            
            <Directory Id="DesktopFolder" Name="Desktop">
                <Component Id="DesktopShortcut" Guid="*">
                    <Condition>{create_desktop} = "yes"</Condition>
                    <Shortcut 
                        Id="DesktopShortcut"
                        Name="{app_name}"
                        Target="[INSTALLDIR]{app_exe}"
                        WorkingDirectory="INSTALLDIR" />
                </Component>
            </Directory>
            
            <Directory Id="ProgramMenuFolder">
                <Directory Id="StartMenuFolder" Name="{app_name}">
                    <Component Id="StartMenuShortcut" Guid="*">
                        <Condition>{create_startmenu} = "yes"</Condition>
                        <Shortcut 
                            Id="StartMenuShortcut"
                            Name="{app_name}"
                            Target="[INSTALLDIR]{app_exe}"
                            WorkingDirectory="INSTALLDIR" />
                        <RemoveFolder Id="StartMenuFolder" On="uninstall" />
                        <RegistryValue Root="HKCU" Key="Software\\{manufacturer}\\{app_name}" Name="installed" Type="integer" Value="1" KeyPath="yes" />
                    </Component>
                </Directory>
            </Directory>
        </Directory>
        
        <Feature Id="MainApplication" Title="{app_name}" Level="1">
            <ComponentRef Id="MainExecutable" />
            <ComponentRef Id="DesktopShortcut" />
            <ComponentRef Id="StartMenuShortcut" />
        </Feature>
        
        <Icon Id="icon.ico" SourceFile="$(var.appDir)\\{app_exe}" />
        <Property Id="ARPPRODUCTICON" Value="icon.ico" />
        
        <WixVariable Id="LicenseRtf" Value="{license_rtf}" />
    </Product>
</Wix>""".strip()
