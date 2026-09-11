#!/usr/bin/env python3
"""
Script de Build do TOSKINSTALLER
Compila a aplicação Python em executável usando Nuitka (primário) ou PyInstaller (fallback)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Cores para output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def check_nuitka():
    """Verifica se Nuitka está instalado"""
    try:
        result = subprocess.run(['python', '-m', 'nuitka', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print_success(f"Nuitka encontrado: {result.stdout.strip().split()[0]}")
            return True
    except Exception:
        pass
    
    print_warning("Nuitka não encontrado")
    return False

def check_pyinstaller():
    """Verifica se PyInstaller está instalado"""
    try:
        result = subprocess.run(['pyinstaller', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print_success(f"PyInstaller encontrado: {result.stdout.strip()}")
            return True
    except Exception:
        pass
    
    print_warning("PyInstaller não encontrado")
    return False

def build_with_nuitka(output_dir='dist'):
    """Build usando Nuitka (recomendado)"""
    print_header("BUILD COM NUKITA")
    
    src_dir = Path('src')
    main_py = src_dir / 'main.py'
    
    if not main_py.exists():
        print_error(f"Arquivo principal não encontrado: {main_py}")
        return False
    
    # Comando Nuitka
    cmd = [
        sys.executable, '-m', 'nuitka',
        '--standalone',
        '--onefile',
        '--windows-disable-console',
        '--windows-icon-from-ico=assets/logos/toskeralab.ico',
        '--product-name=TOSKINSTALLER',
        '--file-description=TOSKINSTALLER - Criador de Pacotes',
        '--company-name=ToskeraLAB',
        f'--output-dir={output_dir}',
        str(main_py)
    ]
    
    print_info(f"Executando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        if result.returncode == 0:
            print_success("Build com Nuitka concluído com sucesso!")
            return True
    except subprocess.CalledProcessError as e:
        print_error(f"Erro no build com Nuitka: {e}")
        return False
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        return False
    
    return False

def build_with_pyinstaller(output_dir='dist'):
    """Build usando PyInstaller (fallback)"""
    print_header("BUILD COM PYINSTALLER (FALLBACK)")
    
    src_dir = Path('src')
    main_py = src_dir / 'main.py'
    
    if not main_py.exists():
        print_error(f"Arquivo principal não encontrado: {main_py}")
        return False
    
    # Espec file para PyInstaller
    spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/ui/resources', 'ui/resources'),
        ('templates', 'templates'),
    ],
    hiddenimports=[
        'PySide6.QtQuick',
        'PySide6.QtQml',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TOSKINSTALLER',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/logos/toskeralab.ico',
)
'''
    
    spec_file = 'toskinstaller.spec'
    with open(spec_file, 'w') as f:
        f.write(spec_content)
    
    print_info(f"Spec file criado: {spec_file}")
    
    cmd = ['pyinstaller', '--clean', '--distpath', output_dir, spec_file]
    
    try:
        result = subprocess.run(cmd, check=True)
        if result.returncode == 0:
            print_success("Build com PyInstaller concluído com sucesso!")
            
            # Limpar spec file
            if os.path.exists(spec_file):
                os.remove(spec_file)
            
            return True
    except subprocess.CalledProcessError as e:
        print_error(f"Erro no build com PyInstaller: {e}")
        return False
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        return False
    
    return False

def main():
    """Função principal"""
    print_header("TOSKINSTALLER - BUILD SCRIPT")
    print_info("Desenvolvido por ToskeraLAB ART/TECH House")
    
    # Verificar diretórios
    if not os.path.exists('src'):
        print_error("Diretório 'src' não encontrado. Execute este script na raiz do projeto.")
        sys.exit(1)
    
    output_dir = 'dist'
    os.makedirs(output_dir, exist_ok=True)
    
    # Tentar Nuitka primeiro
    nuitka_available = check_nuitka()
    pyinstaller_available = check_pyinstaller()
    
    if not nuitka_available and not pyinstaller_available:
        print_error("\nNenhuma ferramenta de build encontrada!")
        print_info("Instale com: pip install nuitka pyinstaller")
        sys.exit(1)
    
    success = False
    
    if nuitka_available:
        success = build_with_nuitka(output_dir)
    
    if not success and pyinstaller_available:
        print_warning("\nFallback para PyInstaller...")
        success = build_with_pyinstaller(output_dir)
    
    if success:
        print_header("BUILD CONCLUÍDO")
        print_success(f"Executável gerado em: {output_dir}/")
        print_info("Para distribuir, inclua também:")
        print_info("  - templates/ (modelos Inno Setup e WiX)")
        print_info("  - assets/ (logos e imagens)")
    else:
        print_error("Build falhou. Verifique os logs acima.")
        sys.exit(1)

if __name__ == '__main__':
    main()
