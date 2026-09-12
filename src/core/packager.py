"""
TOSKINSTALLER - Packager Module
Orquestra a geração de pacotes finais (.EXE, .MSI, Portable)

Copyright (c) 2024 ToskeraLAB ART/TECH House
Licensed under MIT License
"""

import shutil
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime

from src.core.package_result import PackageResult
from src.models.package_config import PackageConfig, OutputFormat
from src.utils.file_utils import FileUtils
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Packager:
    """
    Orquestrador principal para geração de pacotes instaladores.
    
    Responsabilidades:
    - Gerenciar múltiplos formatos de saída simultâneos
    - Coordenar engines de empacotamento (Inno, WiX, Portable)
    - Gerenciar arquivos temporários
    - Aplicar assinatura digital
    - Reportar progresso e resultados
    """
    
    def __init__(self, config: PackageConfig):
        """
        Inicializa o Packager com configuração.
        
        Args:
            config: Configuração do pacote
        """
        self.config = config
        self.temp_dir: Optional[Path] = None
        self.progress_callback: Optional[Callable[[str, int], None]] = None
        self.results: List[PackageResult] = []
        
    def set_progress_callback(self, callback: Callable[[str, int], None]):
        """
        Define callback para reporte de progresso.
        
        Args:
            callback: Função que recebe (mensagem, porcentagem)
        """
        self.progress_callback = callback
        
    def _report_progress(self, message: str, percentage: int = 0):
        """Reporta progresso via callback"""
        logger.info(f"[{percentage}%] {message}")
        if self.progress_callback:
            try:
                self.progress_callback(message, percentage)
            except Exception as e:
                logger.warning(f"Erro no callback de progresso: {e}")
    
    def create_temp_structure(self, source_exe: Path) -> Path:
        """
        Cria estrutura temporária para empacotamento.
        
        Args:
            source_exe: Caminho para o executável fonte
            
        Returns:
            Caminho da pasta temporária
        """
        self.temp_dir = Path(tempfile.mkdtemp(prefix="tosk_pkg_"))
        logger.debug(f"Estrutura temporária criada: {self.temp_dir}")
        
        # Criar subpastas
        app_dir = self.temp_dir / "app"
        app_dir.mkdir(parents=True)
        
        # Copiar executável principal
        dest_exe = app_dir / source_exe.name
        shutil.copy2(source_exe, dest_exe)
        logger.debug(f"Executável copiado para: {dest_exe}")
        
        # Copiar arquivos adicionais se configurado
        if self.config.additional_files:
            for file_path in self.config.additional_files:
                if Path(file_path).exists():
                    dest_path = app_dir / Path(file_path).name
                    shutil.copy2(file_path, dest_path)
                    logger.debug(f"Arquivo adicional copiado: {file_path}")
        
        # Copiar apps parceiros
        if self.config.partner_apps:
            partners_dir = self.temp_dir / "partners"
            partners_dir.mkdir()
            
            for partner in self.config.partner_apps:
                if Path(partner.path).exists():
                    dest_path = partners_dir / Path(partner.path).name
                    shutil.copy2(partner.path, dest_path)
                    logger.debug(f"App parceiro copiado: {partner.path}")
        
        # Copiar recursos de UI (logo, banners)
        self._copy_ui_resources()
        
        return self.temp_dir
    
    def _copy_ui_resources(self):
        """Copia recursos de UI para estrutura temporária"""
        if not self.temp_dir:
            return
            
        resources_dir = self.temp_dir / "resources"
        resources_dir.mkdir()
        
        # Logo
        if self.config.logo_path and Path(self.config.logo_path).exists():
            shutil.copy2(self.config.logo_path, resources_dir / "logo.png")
            
        # Banners
        if self.config.banner_welcome and Path(self.config.banner_welcome).exists():
            shutil.copy2(self.config.banner_welcome, resources_dir / "banner_welcome.png")
        if self.config.banner_complete and Path(self.config.banner_complete).exists():
            shutil.copy2(self.config.banner_complete, resources_dir / "banner_complete.png")
            
        # Licença
        if self.config.license_file and Path(self.config.license_file).exists():
            shutil.copy2(self.config.license_file, resources_dir / "license.txt")
    
    def generate_packages(self, source_exe: Path) -> List[PackageResult]:
        """
        Gera todos os pacotes configurados.
        
        Args:
            source_exe: Caminho para o executável fonte
            
        Returns:
            Lista de resultados de empacotamento
        """
        self.results = []
        self._report_progress("Iniciando geração de pacotes...", 0)
        
        try:
            # Criar estrutura temporária
            self._report_progress("Preparando ambiente temporário...", 5)
            self.create_temp_structure(source_exe)
            
            # Gerar cada formato selecionado
            formats_to_generate = self.config.output_formats
            
            total_formats = len(formats_to_generate)
            
            for i, fmt in enumerate(formats_to_generate):
                progress_base = 10 + (i * 80 // total_formats)
                
                try:
                    self._report_progress(f"Gerando formato {fmt.value}...", progress_base)
                    result = self._generate_format(fmt, source_exe)
                    self.results.append(result)
                    
                    if result.success:
                        self._report_progress(f"{fmt.value} gerado com sucesso", progress_base + 5)
                    else:
                        self._report_progress(f"Falha ao gerar {fmt.value}: {result.error_message}", progress_base + 5)
                        
                except Exception as e:
                    logger.error(f"Erro ao gerar {fmt.value}: {e}")
                    result = PackageResult(
                        success=False,
                        package_type=fmt.value,
                        error_message=str(e)
                    )
                    result.add_log(f"Exceção: {e}")
                    self.results.append(result)
            
            # Assinar pacotes se configurado
            if self.config.enable_signing and self.config.signing_config:
                self._report_progress("Aplicando assinatura digital...", 90)
                self._sign_packages()
            
            # Limpeza
            self._report_progress("Finalizando...", 95)
            self._cleanup()
            
            self._report_progress("Concluído!", 100)
            
        except Exception as e:
            logger.error(f"Erro crítico no empacotamento: {e}")
            self._report_progress(f"Erro crítico: {e}", 0)
            self._cleanup()
            
        return self.results
    
    def _generate_format(self, fmt: OutputFormat, source_exe: Path) -> PackageResult:
        """
        Gera um pacote em formato específico.
        
        Args:
            fmt: Formato de saída
            source_exe: Executável fonte
            
        Returns:
            Resultado do empacotamento
        """
        logger.info(f"Gerando pacote no formato: {fmt.value}")
        
        if fmt == OutputFormat.EXE_INSTALLER:
            return self._generate_inno(source_exe)
        elif fmt == OutputFormat.MSI_INSTALLER:
            return self._generate_wix(source_exe)
        elif fmt == OutputFormat.PORTABLE:
            return self._generate_portable(source_exe)
        else:
            return PackageResult(
                success=False,
                package_type=fmt.value,
                error_message=f"Formato não suportado: {fmt.value}"
            )
    
    def _generate_inno(self, source_exe: Path) -> PackageResult:
        """Gera instalador Inno Setup"""
        from src.engines.inno.inno_builder import InnoBuilder
        
        result = PackageResult(
            success=False,
            package_type='exe',
            app_name=self.config.app_name,
            app_version=self.config.app_version,
            architecture=self.config.architecture,
            temp_folder=self.temp_dir,
            source_exe=source_exe
        )
        
        try:
            builder = InnoBuilder(self.config)
            output_path = builder.build(source_exe, self.temp_dir)
            
            if output_path and output_path.exists():
                result.success = True
                result.package_path = output_path
                result.file_size_bytes = output_path.stat().st_size
                result.add_log(f"Inno Setup gerado: {output_path}")
            else:
                result.error_message = "Inno Setup não gerou arquivo de saída"
                result.add_log("Falha na geração do instalador Inno")
                
        except FileNotFoundError:
            result.error_message = "Inno Setup não encontrado. Instale ou permita download automático."
            result.add_log("Inno Setup não disponível no sistema")
        except Exception as e:
            result.error_message = f"Erro no Inno Setup: {str(e)}"
            result.add_log(f"Exceção: {e}")
            
        return result
    
    def _generate_wix(self, source_exe: Path) -> PackageResult:
        """Gera instalador WiX (MSI)"""
        from src.engines.wix.wix_builder import WixBuilder
        
        result = PackageResult(
            success=False,
            package_type='msi',
            app_name=self.config.app_name,
            app_version=self.config.app_version,
            architecture=self.config.architecture,
            temp_folder=self.temp_dir,
            source_exe=source_exe
        )
        
        try:
            builder = WixBuilder(self.config)
            output_path = builder.build(source_exe, self.temp_dir)
            
            if output_path and output_path.exists():
                result.success = True
                result.package_path = output_path
                result.file_size_bytes = output_path.stat().st_size
                result.add_log(f"WiX MSI gerado: {output_path}")
            else:
                result.error_message = "WiX não gerou arquivo MSI de saída"
                result.add_log("Falha na geração do instalador WiX")
                
        except FileNotFoundError:
            result.error_message = "WiX Toolset não encontrado. Instale ou permita download automático."
            result.add_log("WiX Toolset não disponível no sistema")
        except Exception as e:
            result.error_message = f"Erro no WiX: {str(e)}"
            result.add_log(f"Exceção: {e}")
            
        return result
    
    def _generate_portable(self, source_exe: Path) -> PackageResult:
        """Gera pacote portable"""
        from ..engines.portable.portable_builder import PortableBuilder
        
        result = PackageResult(
            success=False,
            package_type='portable',
            app_name=self.config.app_name,
            app_version=self.config.app_version,
            architecture=self.config.architecture,
            temp_folder=self.temp_dir,
            source_exe=source_exe
        )
        
        try:
            builder = PortableBuilder(self.config)
            output_path = builder.build(source_exe, self.temp_dir)
            
            if output_path and output_path.exists():
                result.success = True
                result.package_path = output_path
                result.file_size_bytes = output_path.stat().st_size
                result.add_log(f"Pacote portable gerado: {output_path}")
            else:
                result.error_message = "Falha ao gerar pacote portable"
                result.add_log("Portable builder não gerou arquivo de saída")
                
        except Exception as e:
            result.error_message = f"Erro no portable builder: {str(e)}"
            result.add_log(f"Exceção: {e}")
            
        return result
    
    def _sign_packages(self):
        """Aplica assinatura digital aos pacotes gerados"""
        from ..tools.sign_tool import SignTool
        
        if not self.config.signing_config:
            logger.warning("Configuração de assinatura ausente")
            return
            
        sign_tool = SignTool(self.config.signing_config)
        
        for result in self.results:
            if result.success and result.package_path:
                try:
                    signed = sign_tool.sign_file(result.package_path)
                    if signed:
                        result.signed = True
                        result.certificate_subject = self.config.signing_config.subject_name
                        result.add_log(f"Arquivo assinado: {result.package_path}")
                    else:
                        result.add_log("Falha na assinatura digital")
                except Exception as e:
                    result.add_log(f"Erro na assinatura: {e}")
                    logger.error(f"Erro ao assinar {result.package_path}: {e}")
    
    def _cleanup(self):
        """Limpa arquivos temporários"""
        if self.temp_dir and self.temp_dir.exists():
            try:
                if not self.config.keep_temp_files:
                    shutil.rmtree(self.temp_dir)
                    logger.debug(f"Temporários limpos: {self.temp_dir}")
                else:
                    logger.info(f"Arquivos temporários mantidos: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"Erro na limpeza: {e}")
    
    def get_successful_results(self) -> List[PackageResult]:
        """Retorna apenas resultados bem-sucedidos"""
        return [r for r in self.results if r.success]
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo da operação"""
        successful = self.get_successful_results()
        failed = [r for r in self.results if not r.success]
        
        return {
            'total_packages': len(self.results),
            'successful': len(successful),
            'failed': len(failed),
            'packages': [r.to_dict() for r in self.results],
            'total_size_mb': sum(r.file_size_mb for r in successful),
            'all_signed': all(r.signed for r in successful) if successful else False
        }
