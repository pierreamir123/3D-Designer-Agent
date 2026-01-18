from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import uuid


@dataclass
class GraphState:
    """Represents the state of the 3D design workflow."""
    
    # Input components
    user_input: str = ""
    uploaded_image: Optional[str] = None
    
    # Analysis results
    blueprint_json: Optional[Dict[str, Any]] = None
    analysis_error: Optional[str] = None
    
    # Code generation results
    generated_bpy_script: Optional[str] = None
    code_generation_error: Optional[str] = None
    
    # Validation results
    stl_file_path: Optional[str] = None
    validation_error: Optional[str] = None
    is_valid: bool = False
    
    # Internal tracking
    session_id: str = ""
    current_step: str = "initial"  # initial, analysis, architect, validation, complete
    
    def __post_init__(self):
        if not self.session_id:
            self.session_id = str(uuid.uuid4())