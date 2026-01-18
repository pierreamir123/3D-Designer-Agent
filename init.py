#!/usr/bin/env python3
"""
Initialization script for the 3D Designer Agent.
This script verifies all components are properly set up.
"""

import sys
import os
from pathlib import Path

# Add the workspace to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def check_dependencies():
    """Check if required packages are available."""
    print("Checking dependencies...")
    
    required_packages = [
        ("langgraph", "langgraph"),
        ("gradio", "gradio"), 
        ("typing", "typing"),
        ("dataclasses", "dataclasses")
    ]
    
    missing_packages = []
    
    for import_name, display_name in required_packages:
        try:
            __import__(import_name)
            print(f"✓ {display_name}")
        except ImportError:
            print(f"✗ {display_name}")
            missing_packages.append(display_name)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install them using: pip install -r requirements.txt")
        return False
    
    return True


def check_structure():
    """Verify the project structure is intact."""
    print("\nChecking project structure...")
    
    required_files = [
        "three_d_designer_agent/__init__.py",
        "three_d_designer_agent/state.py",
        "three_d_designer_agent/analyst_agent.py",
        "three_d_designer_agent/architect_agent.py",
        "three_d_designer_agent/validator_agent.py",
        "three_d_designer_agent/supervisor_agent.py",
        "three_d_designer_agent/workflow.py",
        "three_d_designer_agent/interface.py",
        "main.py",
        "requirements.txt",
        "README.md"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        full_path = Path("3d_designer_agent") / file_path if "__init__.py" in file_path else Path(file_path)
        if not full_path.exists():
            print(f"✗ {file_path}")
            missing_files.append(file_path)
        else:
            print(f"✓ {file_path}")
    
    # Create __init__.py if it doesn't exist
    init_path = Path("three_d_designer_agent/__init__.py")
    if not init_path.exists():
        init_path.touch()
        print(f"✓ Created {init_path}")
    
    if missing_files:
        print(f"\nMissing files: {', '.join(missing_files)}")
        return False
    
    return True


def test_agents():
    """Basic test of agent functionality."""
    print("\nTesting agent imports...")
    
    try:
        from three_d_designer_agent.state import GraphState
        from three_d_designer_agent.analyst_agent import analyst_node
        from three_d_designer_agent.architect_agent import architect_node
        from three_d_designer_agent.validator_agent import validator_node
        from three_d_designer_agent.supervisor_agent import supervisor_node
        from three_d_designer_agent.workflow import create_3d_design_workflow
        
        print("✓ All agents imported successfully")
        
        # Test basic state creation
        state = GraphState(user_input="test cube")
        print(f"✓ State created: {state.user_input}")
        
        return True
    except Exception as e:
        print(f"✗ Error testing agents: {e}")
        return False


def main():
    print("3D Designer Agent - Initialization Check\n")
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Structure", check_structure),
        ("Agents", test_agents)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n--- {check_name} Check ---")
        if not check_func():
            all_passed = False
    
    print(f"\n{'='*50}")
    if all_passed:
        print("✓ All checks passed! The system is ready to run.")
        print("\nTo start the application, run:")
        print("  python main.py")
    else:
        print("✗ Some checks failed. Please resolve the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()