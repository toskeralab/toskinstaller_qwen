"""
TOSKINSTALLER - Portable Builder
Gera pacotes portables usando 7-Zip + stub Python

Copyright (c) 2024 ToskeraLAB ART/TECH House
Licensed under MIT License
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional, List
import zipfile
import tempfile
import os

from src.models.package_config import PackageConfig
from src.core.logger import get_logger

logger = get_logger(__name__)


class PortableBuilder:
    """
    Construtor de pacotes portables.
    
    Estratégia:
    - Comprimir app com 7-Zip ou zipfile puro
    - Criar stub executável que extrai e executa
    - Empacotar tudo em único .exe portable
    
    Para simplicidade inicial, usaremos zipfile + stub Python
    compilado junto com o conteúdo.
    """
    
    def __init__(self, config: PackageConfig):
        """
        Inicializa o builder com configuração.
        
        Args:
            config: Configuração do pacote
        """
        self.config = config
        self.sevenzip_path: Optional[Path] = None
        
    def find_sevenzip(self) -> Optional[Path]:
        """Localiza 7-Zip no sistema"""
        paths = [
            r"C:\Program Files\7-Zip\7z.exe",
            r"C:\Program Files (x86)\7-Zip\7z.exe",
        ]
        
        for path in paths:
            if Path(path).exists():
                self.sevenzip_path = Path(path)
                logger.info(f"7-Zip encontrado: {self.sevenzip_path}")
                return self.sevenzip_path
        
        # Tentar via PATH
        sevenzip = shutil.which("7z.exe")
        if sevenzip:
            self.sevenzip_path = Path(sevenzip)
            return self.sevenzip_path
        
        logger.info("7-Zip não encontrado, usando zipfile puro")
        return None
    
    def build(self, source_exe: Path, temp_dir: Path) -> Optional[Path]:
        """
        Compila pacote portable.
        
        Args:
            source_exe: Executável fonte
            temp_dir: Pasta temporária
            
        Returns:
            Caminho do portable gerado
        """
        logger.info("Iniciando build portable...")
        
        output_dir = temp_dir / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Estrutura do app
        app_dir = temp_dir / "app"
        
        # Nome do arquivo de saída
        portable_name = f"{self.config.app_name}_Portable_{self.config.app_version or '1.0.0'}.exe"
        output_path = output_dir / portable_name
        
        # Método 1: Usar 7-Zip se disponível (mais eficiente)
        if self.sevenzip_path:
            try:
                return self._build_with_7zip(source_exe, temp_dir, output_path)
            except Exception as e:
                logger.warning(f"7-Zip falhou, fallback para zipfile: {e}")
        
        # Método 2: Zipfile puro + stub
        return self._build_with_zipfile(source_exe, temp_dir, output_path)
    
    def _build_with_7zip(self, source_exe: Path, temp_dir: Path, output_path: Path) -> Optional[Path]:
        """Build usando 7-Zip SFX"""
        app_dir = temp_dir / "app"
        
        # Criar arquivo 7z
        archive_path = temp_dir / "app.7z"
        
        cmd = [
            str(self.sevenzip_path),
            "a",
            "-t7z",
            "-m0=lzma2",
            "-mx=9",
            "-mfb=64",
            "-md=32m",
            "-ms=on",
            str(archive_path),
            str(app_dir)
        ]
        
        logger.info(f"7z: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            raise RuntimeError(f"7-Zip falhou: {result.stderr}")
        
        # Criar módulo SFX
        sfx_module = self._find_sfx_module()
        
        if sfx_module:
            # Concatenar SFX + archive
            with open(output_path, 'wb') as out_f:
                # Copiar módulo SFX
                with open(sfx_module, 'rb') as sfx_f:
                    out_f.write(sfx_f.read())
                # Copiar archive 7z
                with open(archive_path, 'rb') as arc_f:
                    out_f.write(arc_f.read())
            
            # Tornar executável
            output_path.chmod(0o755)
            
            logger.info(f"Portable SFX gerado: {output_path}")
            return output_path
        else:
            logger.warning("Módulo SFX não encontrado, usando fallback")
            return self._build_with_zipfile(source_exe, temp_dir, output_path)
    
    def _find_sfx_module(self) -> Optional[Path]:
        """Encontra módulo SFX do 7-Zip"""
        if not self.sevenzip_path:
            return None
        
        sfx_paths = [
            self.sevenzip_path.parent / "7z.sfx",
            self.sevenzip_path.parent / "7zxSD.sfx",
        ]
        
        for path in sfx_paths:
            if path.exists():
                return path
        
        return None
    
    def _build_with_zipfile(self, source_exe: Path, temp_dir: Path, output_path: Path) -> Optional[Path]:
        """
        Build usando zipfile puro + stub Python.
        
        Esta abordagem cria um arquivo ZIP com:
        - Conteúdo do app
        - Stub extractor Python
        - Concatena com header Python para criar .exe auto-extrator
        """
        app_dir = temp_dir / "app"
        
        # Criar ZIP com conteúdo
        zip_path = temp_dir / "app.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Adicionar executável principal
            zf.write(source_exe, source_exe.name)
            
            # Adicionar arquivos adicionais
            for file in app_dir.iterdir():
                if file != source_exe and file.is_file():
                    zf.write(file, file.name)
            
            # Adicionar recursos
            resources_dir = temp_dir / "resources"
            if resources_dir.exists():
                for file in resources_dir.rglob("*"):
                    if file.is_file():
                        arcname = f"resources/{file.relative_to(resources_dir)}"
                        zf.write(file, arcname)
            
            # Adicionar stub extractor
            stub_content = self._generate_stub_script()
            zf.writestr("_extract_and_run.py", stub_content)
        
        # Criar script launcher que será convertido em EXE
        launcher_script = self._generate_launcher(temp_dir, zip_path)
        
        # Para um portable real, precisamos compilar este script
        # Aqui retornamos o ZIP como solução intermediária
        # O usuário final pode executar o stub Python
        
        # Solução melhor: criar um script único que contém ZIP embutido
        single_exe_script = self._create_single_file_extractor(zip_path, source_exe, output_path.with_suffix('.py'))
        
        # Nota: Em produção, este script seria compilado com Nuitka/PyInstaller
        # Por enquanto, retornamos o caminho do script Python
        # O packager deve compilar isso posteriormente
        
        logger.info(f"Script portable gerado: {single_exe_script}")
        
        # Para simplificar, vamos criar o ZIP final que pode ser distribuído
        # com instruções para executar
        final_zip = output_path.with_suffix('.zip')
        shutil.copy2(zip_path, final_zip)
        
        logger.info(f"Portable ZIP gerado: {final_zip}")
        logger.info("Nota: Para .exe portable, compile o script com Nuitka/PyInstaller")
        
        # Retornar ZIP por enquanto
        # Em implementação completa, compilaríamos o stub para .exe
        return final_zip
    
    def _generate_stub_script(self) -> str:
        """Gera script Python para extração e execução"""
        return '''#!/usr/bin/env python3
"""
Stub extractor para pacote portable TOSKINSTALLER
Extrai e executa o aplicativo
"""

import zipfile
import tempfile
import os
import sys
import subprocess
from pathlib import Path

def extract_and_run():
    # Determinar localização do próprio executável
    if getattr(sys, 'frozen', False):
        # Executando como compilado
        own_path = Path(sys.executable)
    else:
        # Executando como script
        own_path = Path(__file__).parent
    
    # Encontrar arquivo ZIP
    zip_files = list(own_path.glob("*.zip"))
    if not zip_files:
        print("Arquivo ZIP não encontrado!")
        return False
    
    zip_path = zip_files[0]
    
    # Extrair para pasta temporária
    temp_dir = Path(tempfile.mkdtemp(prefix="tosk_app_"))
    
    print(f"Extraindo para: {temp_dir}")
    
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(temp_dir)
    
    # Encontrar executável principal
    exe_files = list(temp_dir.glob("*.exe"))
    if not exe_files:
        print("Executável não encontrado!")
        return False
    
    main_exe = exe_files[0]
    
    # Executar
    print(f"Executando: {main_exe}")
    subprocess.run([str(main_exe)])
    
    return True

if __name__ == "__main__":
    extract_and_run()
'''.strip()
    
    def _generate_launcher(self, temp_dir: Path, zip_path: Path) -> str:
        """Gera script launcher"""
        return f'''#!/usr/bin/env python3
import sys
import zipfile
import tempfile
import subprocess
from pathlib import Path

ZIP_PATH = r"{zip_path}"

def main():
    temp_dir = Path(tempfile.mkdtemp(prefix="tosk_"))
    
    with zipfile.ZipFile(ZIP_PATH, 'r') as zf:
        zf.extractall(temp_dir)
    
    exe = list(temp_dir.glob("*.exe"))[0]
    subprocess.run([str(exe)])

if __name__ == "__main__":
    main()
'''
    
    def _create_single_file_extractor(self, zip_path: Path, source_exe: Path, output_script: Path) -> Path:
        """
        Cria script único que contém ZIP embutido como base64.
        Isso permite distribuição como arquivo único.
        """
        import base64
        
        # Ler ZIP como base64
        with open(zip_path, 'rb') as f:
            zip_data = base64.b64encode(f.read()).decode('ascii')
        
        # Dividir em chunks para evitar linhas muito longas
        chunk_size = 80
        zip_chunks = [zip_data[i:i+chunk_size] for i in range(0, len(zip_data), chunk_size)]
        zip_b64 = '\n'.join(zip_chunks)
        
        script_content = f'''#!/usr/bin/env python3
"""
TOSKINSTALLER Portable Launcher
{self.config.app_name} v{self.config.app_version or '1.0.0'}

Este é um executável auto-extrator.
Execute diretamente para iniciar o aplicativo.
"""

import base64
import zipfile
import tempfile
import subprocess
import sys
from pathlib import Path
from io import BytesIO

# Dados ZIP embutidos (base64)
ZIP_DATA_B64 = b\"\"\"
{zip_b64}
\"\"\"

def main():
    try:
        # Decodificar ZIP
        zip_bytes = base64.b64decode(ZIP_DATA_B64)
        zip_buffer = BytesIO(zip_bytes)
        
        # Extrair para temporário
        temp_dir = Path(tempfile.mkdtemp(prefix="{self.config.app_name}_"))
        
        print(f"{{self.config.app_name}} - Extraindo...")
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            zf.extractall(temp_dir)
        
        print(f"Extraído em: {{temp_dir}}")
        print(f"Iniciando {{self.config.app_name}}...")
        
        # Encontrar e executar app principal
        main_exe = temp_dir / "{source_exe.name}"
        
        if main_exe.exists():
            subprocess.run([str(main_exe)], cwd=temp_dir)
        else:
            print(f"Erro: {{main_exe}} não encontrado")
            return False
        
        return True
        
    except Exception as e:
        print(f"Erro: {{e}}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
'''
        
        output_script.write_text(script_content, encoding='utf-8')
        return output_script
