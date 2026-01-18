import gradio as gr
import tempfile
import os
from .workflow import create_3d_design_workflow, approve_blueprint, submit_feedback
from .state import GraphState


class ThreeDDesignerInterface:
    def __init__(self):
        self.workflow = create_3d_design_workflow()
        self.current_state = GraphState()
        
    def process_input(self, user_input, image_upload):
        """Process the user input through the workflow"""
        # Update state with user input
        self.current_state.user_input = user_input
        if image_upload is not None:
            self.current_state.uploaded_image = image_upload.name
        
        # Run the workflow until it reaches the analysis stage
        # In a real implementation, we'd have a way to pause at the human feedback stage
        try:
            # Run the analyst agent first
            if self.current_state.current_step == "initial":
                result = self.workflow.invoke({"user_input": self.current_state.user_input, "uploaded_image": self.current_state.uploaded_image, "current_step": self.current_state.current_step})
                self.current_state = GraphState(**result)
                
            # Return the blueprint for human review
            blueprint_json = self.current_state.blueprint_json
            return (
                gr.update(value=blueprint_json, visible=True),
                gr.update(visible=False),  # Hide 3D model initially
                f"Analysis complete. Found {len(blueprint_json['elements']) if blueprint_json else 0} elements."
            )
        except Exception as e:
            return (
                gr.update(visible=False),
                gr.update(visible=False),
                f"Error: {str(e)}"
            )
    
    def approve_and_generate(self, blueprint_json_str):
        """Approve the blueprint and continue with generation"""
        try:
            import json
            blueprint_json = json.loads(blueprint_json_str)
            
            # Update state with approved blueprint
            self.current_state.blueprint_json = blueprint_json
            self.current_state.current_step = "approved"
            
            # Continue with architect and validator
            result = self.workflow.invoke(vars(self.current_state))
            self.current_state = GraphState(**result)
            
            # Return the STL file for 3D preview
            stl_path = self.current_state.stl_file_path
            if stl_path:
                return (
                    gr.update(visible=True),  # Show 3D model
                    stl_path,
                    "3D model generated successfully!"
                )
            else:
                return (
                    gr.update(visible=False),
                    None,
                    "No STL file generated."
                )
        except Exception as e:
            return (
                gr.update(visible=False),
                None,
                f"Generation error: {str(e)}"
            )
    
    def apply_feedback(self, feedback_text):
        """Apply user feedback to modify the design"""
        try:
            # Submit feedback to the system
            self.current_state = submit_feedback(feedback_text, self.current_state)
            
            # Re-run the workflow
            result = self.workflow.invoke(vars(self.current_state))
            self.current_state = GraphState(**result)
            
            # Return updated blueprint
            blueprint_json = self.current_state.blueprint_json
            return (
                gr.update(value=blueprint_json, visible=True),
                gr.update(visible=False),  # Hide 3D model
                "Feedback applied. Updated blueprint ready for review."
            )
        except Exception as e:
            return (
                gr.update(visible=False),
                gr.update(visible=False),
                f"Feedback error: {str(e)}"
            )
    
    def launch(self):
        with gr.Blocks(title="Autonomous 3D Designer Agent") as demo:
            gr.Markdown("# Autonomous 3D Designer Agent")
            gr.Markdown("Upload an image or describe a 3D object to generate a 3D model.")
            
            with gr.Row():
                with gr.Column():
                    user_input = gr.Textbox(label="Describe your 3D object or provide design instructions", 
                                          placeholder="e.g., 'A cube with a cylindrical hole through the center'", 
                                          lines=3)
                    image_upload = gr.Image(type="filepath", label="Or upload an image for analysis")
                    submit_btn = gr.Button("Generate Design")
                    
                    gr.Markdown("### Design Feedback")
                    feedback_input = gr.Textbox(label="Modify design (e.g., 'make it bigger', 'add a sphere')", 
                                             placeholder="Enter modification instructions",
                                             lines=2)
                    feedback_btn = gr.Button("Apply Feedback")
                
                with gr.Column():
                    status_output = gr.Textbox(label="Status", interactive=False)
            
            # JSON Blueprint Display (for human review)
            with gr.Row(visible=False) as json_row:
                blueprint_display = gr.JSON(label="Generated Blueprint (Review and Approve)")
                approve_btn = gr.Button("Approve & Generate 3D Model")
            
            # 3D Model Display
            with gr.Row(visible=False) as model_row:
                model_output = gr.Model3D(label="Generated 3D Model", interactive=False)
            
            # Event handlers
            submit_btn.click(
                fn=self.process_input,
                inputs=[user_input, image_upload],
                outputs=[blueprint_display, model_output, status_output]
            ).then(
                fn=lambda: gr.update(visible=True),  # Show JSON panel after analysis
                inputs=None,
                outputs=json_row
            )
            
            approve_btn.click(
                fn=self.approve_and_generate,
                inputs=blueprint_display,
                outputs=[model_output, model_output, status_output]
            ).then(
                fn=lambda: gr.update(visible=True),  # Show 3D model after generation
                inputs=None,
                outputs=model_row
            )
            
            feedback_btn.click(
                fn=self.apply_feedback,
                inputs=feedback_input,
                outputs=[blueprint_display, model_output, status_output]
            ).then(
                fn=lambda: gr.update(visible=True),  # Show JSON panel after feedback
                inputs=None,
                outputs=json_row
            )
        
        return demo


def launch_interface():
    """Launch the Gradio interface"""
    designer_interface = ThreeDDesignerInterface()
    demo = designer_interface.launch()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=True)


if __name__ == "__main__":
    launch_interface()