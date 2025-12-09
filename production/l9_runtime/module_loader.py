"""
L9 Module Loader - Auto-discovery and registration

v3.6.1 Gap Fill Patch:
- Fixed module path resolution for all 10 standard modules
- Added error wrapping (module load cannot crash discovery)
- Added checksum logging for debugging
- Enhanced discovery with detailed logging
"""
import importlib
import pkgutil
import logging
import hashlib
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


class ModuleLoader:
    """
    L9 Module Loader
    
    Automatically discovers and loads modules from /modules/ directory.
    Validates module interface compliance (handles + run methods).
    """
    
    def discover_modules(self) -> Dict:
        """
        Discover and load all modules.
        
        Returns:
            Dict of module_name -> module_adapter
        """
        modules = {}
        
        # Get modules directory path
        modules_path = Path(__file__).parent.parent / "modules"
        
        if not modules_path.exists():
            logger.warning(f"Modules directory not found: {modules_path}")
            return modules
        
        logger.info(f"Scanning modules directory: {modules_path}")
        
        # Iterate through module packages
        for _, name, is_pkg in pkgutil.iter_modules([str(modules_path)]):
            if is_pkg:
                logger.debug(f"Found module package: {name}")
                
                # Wrap in try/except to prevent crash
                try:
                    # Import adapter module
                    adapter = importlib.import_module(f"modules.{name}.adapter")
                    
                    # Calculate checksum for debugging
                    adapter_path = Path(modules_path) / name / "adapter.py"
                    checksum = "unknown"
                    if adapter_path.exists():
                        with open(adapter_path, 'rb') as f:
                            checksum = hashlib.md5(f.read()).hexdigest()[:8]
                    
                    # Validate interface compliance
                    if self._validate_module_interface(adapter, name):
                        modules[name] = adapter
                        logger.info(f"✅ Registered module: {name} (checksum: {checksum})")
                    else:
                        logger.warning(f"❌ Module {name} failed interface validation")
                        
                except ImportError as e:
                    logger.warning(f"Could not import module {name}: {e}")
                    # Continue discovery even if one module fails
                except Exception as e:
                    logger.error(f"Error loading module {name}: {e}")
                    # Continue discovery even if one module fails
        
        logger.info(f"Module discovery complete: {len(modules)} modules loaded")
        return modules
    
    def _validate_module_interface(self, module, name: str) -> bool:
        """
        Validate module implements required interface.
        
        Required:
        - handles(command: str) -> bool
        - run(task: dict) -> dict
        
        Args:
            module: Module to validate
            name: Module name for logging
            
        Returns:
            True if valid, False otherwise
        """
        # Check for handles method
        if not hasattr(module, "handles"):
            logger.warning(f"Module {name} missing 'handles' method")
            return False
        
        if not callable(getattr(module, "handles")):
            logger.warning(f"Module {name} 'handles' is not callable")
            return False
        
        # Check for run method
        if not hasattr(module, "run"):
            logger.warning(f"Module {name} missing 'run' method")
            return False
        
        if not callable(getattr(module, "run")):
            logger.warning(f"Module {name} 'run' is not callable")
            return False
        
        logger.debug(f"Module {name} interface validation passed")
        return True
    
    def reload_module(self, module_name: str) -> bool:
        """
        Hot reload a specific module.
        
        Args:
            module_name: Name of module to reload
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Reimport module
            adapter = importlib.import_module(f"modules.{module_name}.adapter")
            importlib.reload(adapter)
            
            # Validate and register
            if self._validate_module_interface(adapter, module_name):
                logger.info(f"Module {module_name} reloaded successfully")
                return True
            else:
                logger.error(f"Module {module_name} failed validation after reload")
                return False
                
        except Exception as e:
            logger.error(f"Module reload failed for {module_name}: {e}")
            return False

