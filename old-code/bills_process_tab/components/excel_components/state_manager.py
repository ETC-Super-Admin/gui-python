# src/components/tabs/bills_process_tab/components/excel_components/state_manager.py
import os
import json
from typing import Set

class StateManager:
    """
    Manages the processing state for Excel files.
    Handles loading and saving of processed file information.
    """
    
    def load_processed_files(self, state_file_path: str) -> Set[str]:
        """
        Load the processing state from the state file.
        
        Args:
            state_file_path: Path to the state file
            
        Returns:
            Set of processed file names
        """
        if not os.path.exists(state_file_path):
            return set()
        
        try:
            with open(state_file_path, "r", encoding="utf-8") as f:
                state = json.load(f)
                if isinstance(state, list):
                    # Handle old format (backward compatibility)
                    return set(state)
                return set(state.get("processed_files", []))
        except (json.JSONDecodeError, IOError):
            return set()

    def save_processed_files(self, state_file_path: str, processed_files: Set[str]):
        """
        Save the processing state to the state file.
        
        Args:
            state_file_path: Path to the state file
            processed_files: Set of processed file names
        """
        try:
            state = {
                "processed_files": list(processed_files)
            }
            with open(state_file_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except IOError as e:
            print(f"Error saving processing state: {e}")