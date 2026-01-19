import gradio as gr
import uuid
from src.graph import app as graph_app
from src.config.logger import get_logger
import os

logger = get_logger("App")

def process_chat(user_input, history, json_data, thread_id, is_initial):
    """
    Main handler for the Chat UI.
    """
    logger.info(f"Chat Triggered: is_initial={is_initial}, thread_id={thread_id}")
    config = {"configurable": {"thread_id": thread_id}}
    
    # Append user message to history immediately for UI feedback
    if history is None:
        history = []
    history.append((user_input, None)) # None for bot response initially
    
    # 1. INITIAL PHASE: User provides description -> Analyst -> Blueprint
    if is_initial:
        logger.info(f"Starting initial analysis with: {user_input[:50]}...")
        inputs = {"input_data": user_input, "messages": []}
        
        try:
            # Run graph until interrupt (after Analyst)
            for event in graph_app.stream(inputs, config=config):
                pass
        except Exception as e:
            err_msg = f"Error during analysis: {str(e)}"
            logger.error(err_msg)
            history[-1] = (user_input, err_msg)
            return history, {}, None, None, True

        # Fetch state
        snapshot = graph_app.get_state(config)
        vals = snapshot.values
        blueprint = vals.get("json_blueprint", {})
        code = vals.get("bpy_code", "")
        
        bot_msg = "I've analyzed your request. Please review the **Blueprint** on the right.\n\nIf it looks good, type **'Proceed'** or **'Build'**. If you want changes, just tell me (e.g., 'Make it taller')."
        history[-1] = (user_input, bot_msg)
        
        return (
            history,            # Updated Chat
            blueprint,          # JSON Output
            None,               # 3D Model (None)
            None,               # Download (None)
            False,              # is_initial -> False
            code                # BPY Code
        )

    # 2. FEEDBACK LOOP: User feedback -> Supervisor -> Architect/Analyst -> Validator
    else:
        logger.info(f"Resuming with feedback: {user_input[:50]}...")
        
        # Update state with potentially modified JSON and new feedback
        graph_app.update_state(config, {"json_blueprint": json_data, "feedback": user_input})
        
        # Resume execution
        # We send None to resume from the interrupt state
        try:
            for event in graph_app.stream(None, config=config):
                # We could stream partial status updates to chat here if we wanted
                pass
        except Exception as e:
            err_msg = f"Error during generation: {str(e)}"
            logger.error(err_msg)
            history[-1] = (user_input, err_msg)
            return history, {}, None, None, False, ""

        # Fetch final state
        snapshot = graph_app.get_state(config)
        vals = snapshot.values
        final_stl = vals.get("stl_path")
        errors = vals.get("errors", [])
        final_code = vals.get("bpy_code", "")

        if final_stl:
            msg = f"✅ **Generation Complete!**\n\nI've generated the 3D model. You can preview it on the right or download the STL file.\nSaved to: `{os.path.basename(final_stl)}`"
            if errors:
                msg += f"\n\n⚠️ **Note:** There were some non-critical issues: {errors}"
            history[-1] = (user_input, msg)
            return history, vals.get("json_blueprint", {}), final_stl, final_stl, False, final_code
        
        elif errors:
            msg = f"❌ **Generation Failed**\n\nThe Validator reported errors:\n" + "\n".join([f"- {e}" for e in errors])
            msg += "\n\nPlease try rephrasing your request."
            history[-1] = (user_input, msg)
            return history, vals.get("json_blueprint", {}), None, None, False, final_code
        
        else:
            # If we looped back to Analyst (interrupted again)
            if snapshot.next and "analyst" in snapshot.next:
                # Should not happen if interrupt is AFTER analyst, but if we route supervisor->analyst->interrupt
                bot_msg = "I've updated the plan based on your feedback. Please review the new Blueprint."
                history[-1] = (user_input, bot_msg)
                return history, vals.get("json_blueprint", {}), None, None, False, final_code
            
            # Catch-all
            history[-1] = (user_input, "Processing complete, but no STL was returned. Check logs.")
            return history, vals.get("json_blueprint", {}), None, None, False, final_code


with gr.Blocks(title="3D Designer Agent", theme=gr.themes.Soft(primary_hue="blue", secondary_hue="slate")) as demo:
    gr.Markdown("# 🛠️ Autonomous 3D Designer Agent")
    
    # Session State
    thread_state = gr.State(lambda: str(uuid.uuid4()))
    is_initial_state = gr.State(True)

    with gr.Row(equal_height=True):
        # LEFT COLUMN: Chat Interface
        with gr.Column(scale=1):
            chatbot = gr.Chatbot(
                label="Designer Assistant", 
                height=600,
                avatar_images=(None, "https://api.dicebear.com/7.x/bottts/svg?seed=3dagent"),
                bubble_full_width=False
            )
            with gr.Row():
                msg_input = gr.Textbox(
                    show_label=False, 
                    placeholder="Describe a 3D object (e.g. 'A simple coffee mug')...",
                    scale=4,
                    container=False
                )
                submit_btn = gr.Button("Send", variant="primary", scale=1)
            
            gr.Examples(
                examples=["A futuristic chair with 3 legs", "A simple red cube", "A chess pawn"],
                inputs=msg_input
            )

        # RIGHT COLUMN: Inspector (Blueprint & 3D View)
        with gr.Column(scale=1):
            with gr.Tabs():
                with gr.TabItem("3D Preview"):
                    model_output = gr.Model3D(
                        label="Model Preview", 
                        clear_color=[0.1, 0.1, 0.1, 1.0], 
                        interactive=True,
                        height=400
                    )
                    download_output = gr.File(label="Download Generated STL")
                
                with gr.TabItem("Blueprint (JSON)"):
                    json_output = gr.JSON(label="Reverse Engineering Plan", height=400)
                    
                with gr.TabItem("Generated Code"):
                    code_output = gr.Code(label="BPY Script", language="python", lines=20)
                    
    # Event Handlers
    submit_btn.click(
        process_chat,
        inputs=[msg_input, chatbot, json_output, thread_state, is_initial_state],
        outputs=[chatbot, json_output, model_output, download_output, is_initial_state, code_output]
    ).then(
        lambda: "", None, msg_input # Clear input box
    )
    
    msg_input.submit(
        process_chat,
        inputs=[msg_input, chatbot, json_output, thread_state, is_initial_state],
        outputs=[chatbot, json_output, model_output, download_output, is_initial_state, code_output]
    ).then(
        lambda: "", None, msg_input
    )

if __name__ == "__main__":
    demo.launch()
