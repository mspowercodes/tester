import streamlit as st
import sys
import io
import traceback
import inspect

st.set_page_config(
    page_title="Line Number Sandbox",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Interactive Python Function Sandbox")
st.markdown("Define your encryption function below. Line numbers are displayed down the left margin!")

# Default template code
default_code = """def caesar_shift3(message):
    table = str.maketrans("abcdefghijklmnopqrstuvwxyz", "DEFGHIJKLMNOPQRSTUVWXYZABC")
    return message.translate(table)
"""

# Establish global track state to remember what the user types
if "code_text" not in st.session_state:
    st.session_state.code_text = default_code
if "exec_env" not in st.session_state:
    st.session_state.exec_env = {}
if "detected_functions" not in st.session_state:
    st.session_state.detected_functions = []

# Create our two main panels: Left for writing code, Right for checking results
col_left_panel, col_right_panel = st.columns(2)

with col_left_panel:
    st.subheader("Input Python Script")
    
    # 1. FIX: Pass weights [1, 25] to make the numbers fit perfectly on the left side
    col_numbers, col_textarea = st.columns([1, 25])
    
    with col_numbers:
        # Pushes the numbers down slightly so they match up perfectly with line 1 of the typing box
        st.markdown("<div style='height: 43px;'></div>", unsafe_allowed_html=True)
        
        # Build a stationary vertical list of 1 to 15 line numbers
        numbers_layout = "<div style='border-right: 1px solid #444; padding-right: 5px;'>"
        for i in range(1, 16):
            numbers_layout += f"<div style='line-height: 25.5px; font-family: monospace; color: #888; text-align: right;'>{i}</div>"
        numbers_layout += "</div>"
            
        st.markdown(numbers_layout, unsafe_allowed_html=True)
        
    with col_textarea:
        with st.form(key="code_form"):
            user_code = st.text_area(
                label="Your Python Script (Max 15 lines visible at once):",
                value=st.session_state.code_text,
                height=385,  # This height lines up perfectly with our 15 vertical numbers
                label_visibility="visible"
            )
            submit_button = st.form_submit_button(label="🚀 Activate My Function")

with col_right_panel:
    st.subheader("Live Output Testing")
    
    if submit_button:
        output_buffer = io.StringIO()
        sys.stdout = output_buffer
        current_env = {}
        
        try:
            # Run the code blocks to fetch the functions
            exec(user_code, current_env)
            
            found_funcs = [
                name for name, obj in current_env.items() 
                if inspect.isfunction(obj) and not name.startswith('__')
            ]
            
            sys.stdout = sys.__stdout__
            st.session_state.exec_env = current_env
            st.session_state.detected_functions = found_funcs
            
        except Exception as e:
            sys.stdout = sys.__stdout__
            st.error("❌ Python Execution Error:")
            st.code(traceback.format_exc(), language="python")

    # --- LIVE INTERACTION ZONE ---
    if st.session_state.detected_functions:
        target_func_name = st.session_state.detected_functions
        target_func = st.session_state.exec_env[target_func_name]
        
        st.success(f"🎉 Active function ready: `{target_func_name}()`")
        st.write("---")
        st.write("### 🧪 Test Your Code Live")
        
        test_input = st.text_input("Enter text to pass into your function:", value="hello world")
        
        try:
            live_result = target_func(test_input)
            st.write("**Function Output:**")
            st.info(f"`{live_result}`")
        except Exception as e:
            st.error(f"Error running `{target_func_name}`: {e}")
    else:
        st.caption("Awaiting successful function build from the left panel...")
