#!/usr/bin/env python3
"""
TOSKINSTALLER - Portable Stub Template
Template para gerador de pacotes portables

Copyright (c) 2024 ToskeraLAB ART/TECH House
Licensed under MIT License

Este script é usado como base para gerar o stub extractor
que será compilado junto com os dados do aplicativo.
"""

import base64
import zipfile
import tempfile
import subprocess
import sys
import os
from pathlib import Path
from io import BytesIO

# ============================================
# DADOS ZIP EMBUTIDOS (BASE64)
# O builder substituirá esta seção com os dados reais
# ============================================
ZIP_DATA_B64 = b"""
{{ZIP_DATA_PLACEHOLDER}}
"""

# ============================================
# METADADOS DO APLICATIVO
# ============================================
APP_NAME = "{{APP_NAME}}"
APP_VERSION = "{{APP_VERSION}}"
APP_EXE = "{{APP_EXE}}"
APP_PUBLISHER = "{{APP_PUBLISHER}}"

# ============================================
# CONFIGURAÇÕES
# ============================================
# Se True, extrai em pasta permanente ao invés de temp
PERSISTENT_MODE = False
# Pasta base para modo persistente (None usa AppData)
PERSISTENT_FOLDER = None


def get_extraction_folder() -> Path:
    """Determina pasta de extração baseada no modo"""
    if PERSISTENT_MODE:
        if PERSISTENT_FOLDER:
            folder = Path(PERSISTENT_FOLDER)
        else:
            # Usar AppData Local
            appdata = os.environ.get('LOCALAPPDATA', os.environ.get('APPDATA', ''))
            folder = Path(appdata) / APP_NAME / 'app'
        
        folder.mkdir(parents=True, exist_ok=True)
        return folder
    else:
        # Modo temporário
        return Path(tempfile.mkdtemp(prefix=f"{APP_NAME}_"))


def extract_app(zip_buffer: BytesIO, dest_folder: Path) -> bool:
    """
    Extrai aplicativo do buffer ZIP para pasta de destino.
    
    Args:
        zip_buffer: Buffer contendo dados ZIP
        dest_folder: Pasta para extração
        
    Returns:
        True se sucesso, False caso contrário
    """
    try:
        print(f"[{APP_NAME}] Extraindo arquivos...")
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            # Extrair todos os arquivos
            zf.extractall(dest_folder)
            
            # Definir permissões (Windows não precisa, mas manter compatibilidade)
            for file_path in dest_folder.rglob("*"):
                if file_path.is_file():
                    try:
                        file_path.chmod(0o755)
                    except:
                        pass
        
        print(f"[{APP_NAME}] Extraído em: {dest_folder}")
        return True
        
    except zipfile.BadZipFile as e:
        print(f"[{APP_NAME}] Erro: Arquivo ZIP corrompido - {e}")
        return False
    except Exception as e:
        print(f"[{APP_NAME}] Erro na extração: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_app(app_folder: Path, exe_name: str) -> int:
    """
    Executa o aplicativo principal.
    
    Args:
        app_folder: Pasta onde o app foi extraído
        exe_name: Nome do executável principal
        
    Returns:
        Código de retorno do processo
    """
    main_exe = app_folder / exe_name
    
    if not main_exe.exists():
        print(f"[{APP_NAME}] Erro: Executável não encontrado: {main_exe}")
        return -1
    
    print(f"[{APP_NAME}] Iniciando {exe_name}...")
    
    try:
        # Executar e aguardar término
        result = subprocess.run(
            [str(main_exe)],
            cwd=app_folder,
            shell=False
        )
        
        return result.returncode
        
    except FileNotFoundError:
        print(f"[{APP_NAME}] Erro: Não foi possível executar {main_exe}")
        return -1
    except PermissionError:
        print(f"[{APP_NAME}] Erro: Permissão negada para executar {main_exe}")
        return -1
    except Exception as e:
        print(f"[{APP_NAME}] Erro ao executar: {e}")
        return -1


def cleanup(extraction_folder: Path, persistent: bool):
    """
    Limpa arquivos temporários após execução.
    
    Args:
        extraction_folder: Pasta extraída
        persistent: Se True, mantém arquivos
    """
    if persistent:
        print(f"[{APP_NAME}] Arquivos mantidos em: {extraction_folder}")
        return
    
    try:
        import shutil
        shutil.rmtree(extraction_folder, ignore_errors=True)
        print(f"[{APP_NAME}] Arquivos temporários limpos")
    except Exception as e:
        print(f"[{APP_NAME}] Aviso: Não foi possível limpar temporários: {e}")


def show_welcome():
    """Exibe mensagem de boas-vindas"""
    banner = f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   {APP_NAME:<30}                         ║
║   Versão: {APP_VERSION:>22}                   ║
║                                                          ║
║   Criado com TOSKINSTALLER                               ║
║   ToskeraLAB ART/TECH House                              ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """
    print(banner)


def main() -> int:
    """
    Função principal do stub portable.
    
    Fluxo:
    1. Decodificar dados ZIP embutidos
    2. Extrair para pasta (temp ou permanente)
    3. Executar aplicativo principal
    4. Limpar (se modo temporário)
    
    Returns:
        Código de retorno (0 = sucesso)
    """
    show_welcome()
    
    try:
        # Passo 1: Decodificar ZIP
        print(f"[{APP_NAME}] Carregando dados...")
        zip_bytes = base64.b64decode(ZIP_DATA_B64)
        zip_buffer = BytesIO(zip_bytes)
        
        # Passo 2: Determinar pasta de extração
        extraction_folder = get_extraction_folder()
        
        # Passo 3: Extrair arquivos
        if not extract_app(zip_buffer, extraction_folder):
            return 1
        
        # Passo 4: Executar aplicativo
        exit_code = run_app(extraction_folder, APP_EXE)
        
        # Passo 5: Limpeza
        cleanup(extraction_folder, PERSISTENT_MODE)
        
        return exit_code if exit_code >= 0 else 1
        
    except KeyboardInterrupt:
        print(f"\n[{APP_NAME}] Operação cancelada pelo usuário")
        return 130
    except Exception as e:
        print(f"[{APP_NAME}] Erro crítico: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
