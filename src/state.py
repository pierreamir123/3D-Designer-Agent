from typing import List, Dict, Any, Optional, TypedDict
from langchain_core.messages import BaseMessage

class GraphState(TypedDict):
    input_data: str  # User description or image path
    json_blueprint: Dict[str, Any]  # The structured 3D plan
    reasoning: str # Chain-of-Thought reasoning from Analyst
    bpy_code: str  # The generated Blender Python code
    stl_path: str  # Path to the exported STL
    feedback: str  # User feedback string
    errors: List[str]  # Validation errors
    mesh_issues: List[str] # Procedural mesh analysis results
    test_report: str # Detailed testing report for iteration
    messages: List[BaseMessage]  # Chat history
    retry_count: int # Track number of self-correction attempts
