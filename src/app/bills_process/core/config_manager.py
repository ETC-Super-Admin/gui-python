import os
from .result import Result
from src.db.config_queries import get_config
from src.db.path_config_queries import get_all_path_configs

class ConfigManager:
    """
    Handles loading and validation of bills processing configuration from the database.
    """
    def load_config(self) -> Result:
        """
        Load and validate the bills processing configuration.
        
        Returns:
            Result: Contains a config dict on success, or an error message on failure.
        """
        try:
            # Get the default inventory code from the general app config
            default_inventory_code = get_config("bills_process_inventory_code")
            if not default_inventory_code:
                return Result.error("❌ Default inventory code is not set. Please set it in the 'Path Configuration' settings.")

            # Get all available path configurations
            all_paths = get_all_path_configs()
            if not all_paths:
                return Result.error("❌ No path configurations found. Please add one in the 'Path Configuration' settings.")

            # Find the template directory for the default inventory code
            template_dir = None
            for path_config in all_paths:
                if path_config['inventory_code'] == default_inventory_code:
                    template_dir = path_config['template_dir']
                    break
            
            if not template_dir:
                return Result.error(f"❌ Path for the default inventory code '{default_inventory_code}' not found. Please check your 'Path Configuration' settings.")

            # Normalize the path to ensure consistent separators
            normalized_path = os.path.normpath(template_dir)

            return Result.success({
                "base_path": normalized_path,
                "inventory_code": default_inventory_code
            })

        except Exception as e:
            return Result.error(f"❌ An unexpected error occurred while loading configuration: {e}")
