#!/usr/bin/env python3
"""
Main entry point for the Autonomous 3D Designer Agent.
This script initializes and runs the LangGraph-based workflow with a Gradio interface.
"""

import argparse
from pathlib import Path
import sys

# Add the workspace to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from three_d_designer_agent.interface import launch_interface


def main():
    parser = argparse.ArgumentParser(description="Autonomous 3D Designer Agent")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host for the Gradio server")
    parser.add_argument("--port", type=int, default=7860, help="Port for the Gradio server")
    parser.add_argument("--share", action="store_true", help="Create a public share link")
    
    args = parser.parse_args()
    
    print("Starting Autonomous 3D Designer Agent...")
    print(f"Server will run on {args.host}:{args.port}")
    if args.share:
        print("A public share link will be created.")
    
    launch_interface()


if __name__ == "__main__":
    main()