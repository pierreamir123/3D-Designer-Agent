import gradio as gr
import uuid
from src.graph import app as graph_app
import os

# Create a unique thread ID for this session (for simplicity, one global session for now, 
# or 1 per page load if we could, but Gradio state is better)
# We'll stick to a generated UUID stored in gr.State

def process_input(user_input, thread_id, current_state):
    config = {"configurable": {"thread_id": thread_id}}
    
    # Check if we are starting fresh or resuming
    if not current_state:
        # Starting fresh
        inputs = {"input_data": user_input, "messages": []}
        # Run until interrupt
        for event in graph_app.stream(inputs, config=config):
            pass # We just want it to reach the interrupt
            
        # Fetch state snapshot
        snapshot = graph_app.get_state(config)
        state_values = snapshot.values
        
        return (
            state_values.get("json_blueprint"), 
            None, # No 3D model yet
            "Analysis Complete. Please review the Blueprint.",
            state_values
        )
    else:
        # Resuming with feedback
        # Update state with feedback
        # We need to update the state. Since 'analyst' was the last node (interrupt after),
        # we are sitting between 'analyst' and 'router'.
        # We want to update 'feedback' and optionally 'json_blueprint' if user edited it.
        # But 'process_input' receives text. 
        # If the user edited the JSON in the UI, we need that too. 
        # Wait, the prompt says "JSON View... changes reverse engineering during interrupt".
        
        # We can use `graph_app.update_state` to patch the state.
        pass

def run_step(message, json_data, thread_id, is_initial):
    config = {"configurable": {"thread_id": thread_id}}
    
    if is_initial:
        # User entered description/image path
        inputs = {"input_data": message, "messages": []}
        # Iterate until interrupt
        for event in graph_app.stream(inputs, config=config):
            pass
            
        snapshot = graph_app.get_state(config)
        vals = snapshot.values
        return (
            vals.get("json_blueprint", {}),
            None,
            "Blueprint generated. Review and Edit JSON, then click Continue.",
            False # is_initial set to False
        )
    else:
        # Resuming
        # Update state with the (potentially modified) JSON and feedback
        graph_app.update_state(config, {"json_blueprint": json_data, "feedback": message})
        
        # Resume
        # We send None to resume from interrupt
        results = []
        final_stl = None
        msgs = []
        
        for event in graph_app.stream(None, config=config):
            # event is dictionary of node_name: value
            for key, value in event.items():
                if "stl_path" in value:
                     final_stl = value["stl_path"]
                if "messages" in value:
                    msgs.extend(value["messages"])
        
        snapshot = graph_app.get_state(config)
        vals = snapshot.values
        final_stl = vals.get("stl_path", final_stl)
        
        status_msg = "Generation Complete." if final_stl else "Processing..."
        if vals.get("errors"):
            status_msg = f"Errors: {vals['errors']}"
            
        # Check if we looped back to analyst (if supervisor routed validation fail or structural change)
        if snapshot.next and "analyst" in snapshot.next:
             # We went back to analyst? No, next would be what's coming.
             # If we are back at 'interrupt', we should stop? 
             # But interrupt is only configured after 'analyst'.
             # If graph loop: Architect -> Validator -> Architect, it runs.
             # If Supervisor -> Analyst, it runs Analyst, sets interrupt again.
             pass
             
        # If we are interrupted again (back at Analyst), we should return control
        if snapshot.next and len(snapshot.next) > 0 and snapshot.created_at: 
             # Check if we are pausing. 
             # stream() yields events. 
             pass

        return (
            vals.get("json_blueprint", {}),
            final_stl,
            status_msg,
            False 
        )

with gr.Blocks(title="3D Designer Agent") as demo:
    gr.Markdown("# Autonomous 3D Designer Agent")
    
    thread_state = gr.State(str(uuid.uuid4()))
    is_initial_state = gr.State(True)
    
    with gr.Row():
        with gr.Column(scale=1):
            msg_input = gr.Textbox(label="Instruction / Feedback", placeholder="Describe 3D object...")
            submit_btn = gr.Button("Submit / Continue")
            status_output = gr.Markdown("Ready")
            
        with gr.Column(scale=1):
            json_output = gr.JSON(label="Blueprint (Editable)")
            model_output = gr.Model3D(label="3D Preview", clear_color=[0.0, 0.0, 0.0, 0.0])

    submit_btn.click(
        run_step,
        inputs=[msg_input, json_output, thread_state, is_initial_state],
        outputs=[json_output, model_output, status_output, is_initial_state]
    )

if __name__ == "__main__":
    demo.launch()
