from typing import List, Dict, Any, Optional, TypedDict
from langchain_core.messages import BaseMessage

class GraphState(TypedDict):
    input_data: str  # User description or image path
    json_blueprint: Dict[str, Any]  # The structured 3D plan
    bpy_code: str  # The generated Blender Python code
    stl_path: str  # Path to the exported STL
    feedback: str  # User feedback string
    errors: List[str]  # Validation errors
    messages: List[BaseMessage]  # Chat history
    revision_count: int # Track number of iterations
