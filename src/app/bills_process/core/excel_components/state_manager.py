import os
import json
from typing import Set

class StateManager:
    """
    Manages the processing state for Excel files, tracking which daily
    files have already been added to the monthly template.
    """
    
    def load_processed_files(self, state_file_path: str) -> Set[str]:
        """
        Load the set of processed file names from the state file.
        """
        if not os.path.exists(state_file_path):
            return set()
        
        try:
            with open(state_file_path, "r", encoding="utf-8") as f:
                state = json.load(f)
                return set(state.get("processed_files", []))
        except (json.JSONDecodeError, IOError):
            return set()

    def save_processed_files(self, state_file_path: str, processed_files: Set[str]):
        """
        Save the updated set of processed file names to the state file.
        """
        try:
            state = {
                "processed_files": sorted(list(processed_files)) # Sort for consistency
            }
            with open(state_file_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except IOError as e:
            print(f"Error saving processing state: {e}")
