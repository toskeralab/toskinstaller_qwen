"""
TOSKINSTALLER - Instalador Automático de Ferramentas

Baixa e instala automaticamente ferramentas externas quando necessário.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple
import requests

from src.core.logger import get_logger

logger = get_logger(__name__)


class ToolInstaller:
    """
    Instalador automático de ferramentas externas.
    
    Suporta download e instalação silenciosa de:
    - Inno Setup
    - WiX Toolset
    - 7-Zip
    - PyInstaller (via pip)
    - Nuitka (via pip)
    """
    
    TOOLS_INFO = {
        'inno_setup': {
            'name': 'Inno Setup',
            'url': 'https://jrsoftware.org/download/iscrypt.exe',
            'silent_args': '/VERYSILENT /NORESTART',
            'check_cmd': 'iscc',
        },
        'wix_toolset': {
            'name': 'WiX Toolset',
            'url': 'https://github.com/wixtoolset/wix3/releases/download/wix3141rtm/wix314.exe',
            'silent_args': '/quiet',
            'check_cmd': 'heat',
        },
        'seven_zip': {
            'name': '7-Zip',
            'url': 'https://www.7-zip.org/a/7z2301-x64.exe',
            'silent_args': '/S',
            'check_cmd': '7z',
        },
        'pyinstaller': {
            'name': 'PyInstaller',
            'pip': True,
            'package': 'pyinstaller',
        },
        'nuitka': {
            'name': 'Nuitka',
            'pip': True,
            'package': 'nuitka',
        },
    }
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def is_installed(self, tool_key: str) -> bool:
        """Verifica se ferramenta está instalada."""
        info = self.TOOLS_INFO.get(tool_key)
        if not info:
            return False
        
        # Ferramentas via pip
        if info.get('pip'):
            try:
                package = info['package']
                if package == 'pyinstaller':
                    import PyInstaller
                    return True
                elif package == 'nuitka':
                    import nuitka
                    return True
                return False
            except ImportError:
                return False
        
        # Ferramentas sistema
        check_cmd = info.get('check_cmd')
        if check_cmd:
            import shutil
            return shutil.which(check_cmd) is not None
        
        return False
    
    def install(self, tool_key: str, progress_callback=None) -> Tuple[bool, str]:
        """
        Instala ferramenta.
        
        Returns:
            Tuple (sucesso, mensagem)
        """
        info = self.TOOLS_INFO.get(tool_key)
        if not info:
            return False, f"Ferramenta desconhecida: {tool_key}"
        
        name = info['name']
        self.logger.info(f"Iniciando instalação de {name}")
        
        try:
            # Ferramentas via pip
            if info.get('pip'):
                return self._install_pip(info, progress_callback)
            
            # Download e instalação de executável
            return self._install_exe(info, progress_callback)
            
        except Exception as e:
            error_msg = f"Erro na instalação de {name}: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def _install_pip(self, info: dict, callback=None) -> Tuple[bool, str]:
        """Instala pacote via pip."""
        package = info['package']
        name = info['name']
        
        if callback:
            callback(f"Instalando {name} via pip...")
        
        cmd = ["pip", "install", "-U", package]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )
            self.logger.info(f"{name} instalado com sucesso")
            return True, f"{name} instalado com sucesso"
        except subprocess.CalledProcessError as e:
            return False, f"Erro pip: {e.stderr}"
    
    def _install_exe(self, info: dict, callback=None) -> Tuple[bool, str]:
        """Baixa e instala executável."""
        name = info['name']
        url = info['url']
        silent_args = info.get('silent_args', '/S')
        
        if callback:
            callback(f"Baixando {name}...")
        
        # Download
        with tempfile.NamedTemporaryFile(delete=False, suffix='.exe') as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            response = requests.get(url, stream=True)
            total = int(response.headers.get('content-length', 0))
            
            with open(tmp_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if callback and total > 0:
                        progress = (downloaded / total) * 100
                        callback(f"Baixando {name}: {progress:.1f}%")
            
            if callback:
                callback(f"Instalando {name}...")
            
            # Executar instalador
            cmd = [str(tmp_path)] + silent_args.split()
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutos timeout
            )
            
            # Limpar temp
            try:
                tmp_path.unlink()
            except:
                pass
            
            if result.returncode == 0:
                self.logger.info(f"{name} instalado com sucesso")
                return True, f"{name} instalado com sucesso"
            else:
                return False, f"Erro na instalação: {result.stderr}"
                
        except requests.RequestException as e:
            return False, f"Erro no download: {str(e)}"
        except subprocess.TimeoutExpired:
            return False, "Timeout na instalação"
        finally:
            # Limpeza final
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except:
                    pass
    
    def get_download_url(self, tool_key: str) -> Optional[str]:
        """Retorna URL de download da ferramenta."""
        info = self.TOOLS_INFO.get(tool_key)
        if info:
            return info.get('url') or f"pip install {info.get('package', '')}"
        return None
    
    def get_instructions(self, tool_key: str) -> str:
        """Retorna instruções de instalação manual."""
        info = self.TOOLS_INFO.get(tool_key)
        if not info:
            return "Ferramenta desconhecida"
        
        if info.get('pip'):
            return f"Execute: pip install -U {info['package']}"
        
        return f"""
Instruções para instalar {info['name']}:

1. Acesse: {info.get('url', 'site oficial')}
2. Baixe o instalador
3. Execute o instalador
4. Adicione ao PATH do sistema se necessário

Ou use a instalação automática do TOSKINSTALLER.
"""
