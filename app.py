import streamlit as st
import subprocess
import json
import os

def trigger_generation_in_tmux(headings, mode="slides", template_type=None, json_data=None):
    """
    Sends a command to the GPU-allocated tmux session named 'gpu_session'.
    This command runs run_generation.py with the provided parameters.
    
    Args:
        headings (str): Slide headings or empty string for grant proposal
        mode (str): "slides" or "grant" to determine which generation to run
        template_type (str): "proposal" or "rfp" for grant mode
        json_data (str): JSON data for grant proposal generation
    """
    # Escape quotes in the parameters so they pass correctly to the shell
    escaped_headings = headings.replace('"', r'\"') if headings else ""
    
    # Build the command based on the mode
    if mode == "slides":
        cmd = f'tmux send-keys -t 0 "python run_generation.py --mode slides --headings \\"{escaped_headings}\\" " Enter'
    else:  # grant proposal mode
        escaped_json = json_data.replace('"', r'\"') if json_data else ""
        cmd = f'tmux send-keys -t 0 "python run_generation.py --mode grant --template_type {template_type} --json_data \\"{escaped_json}\\" " Enter'
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        st.error(f"Error triggering generation in tmux: {e}")
        return False

def load_template(template_type):
    """Load the specified JSON template."""
    template_file = f"grant_{template_type}_template.json"
    try:
        with open(template_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading template: {e}")
        return None

# Set up the main app
st.title("Content Generator UI")

# Create tabs for different generation options
tab1, tab2 = st.tabs(["Generate Slides", "Grant Proposal"])

# Slide Generation Tab
with tab1:
    st.header("Slide Generator")
    headings_input = st.text_area("Enter your slide headings (each on a new line):")
    
    if st.button("Generate Slides"):
        if headings_input.strip():
            st.info("Triggering GPU generation in the allocated tmux session...")
            success = trigger_generation_in_tmux(headings_input, mode="slides")
            if success:
                st.success("Generation triggered! Check the GPU session logs for progress.")
                st.info("Once complete, you can download the generated presentation from the designated output directory.")
        else:
            st.error("Please enter valid slide headings.")

# Grant Proposal Tab
with tab2:
    st.header("Grant Proposal Generator")
    
    template_type = st.radio(
        "Select template type:",
        ["proposal", "rfp"]
    )
    
    # Load and display the selected template
    template = load_template(template_type)
    
    if template:
        st.subheader("Fill in the template")
        
        # Create input fields based on the template structure
        json_input = {}
        
        for key, value in template.items():
            if isinstance(value, dict):
                st.subheader(key)
                json_input[key] = {}
                
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, str):
                        json_input[key][subkey] = st.text_area(f"{subkey}", subvalue)
            elif isinstance(value, str):
                json_input[key] = st.text_area(f"{key}", value)
        
        if st.button("Generate Grant Document"):
            st.info("Sending to Claude for optimization...")
            
            # Convert the filled template to JSON
            json_data = json.dumps(json_input)
            
            # Trigger the generation
            success = trigger_generation_in_tmux("", mode="grant", template_type=template_type, json_data=json_data)
            
            if success:
                st.success("Generation triggered! Check the GPU session logs for progress.")
                st.info("Once complete, you can download the generated document from the designated output directory.")
    else:
        st.error(f"Could not load the {template_type} template.")