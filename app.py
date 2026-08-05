import streamlit as st
import sys
import io
import traceback
import ast
import inspect

st.set_page_config(
    page_title="Line Number Python Sandbox",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Python Sandbox with Line Numbers")
st.markdown("Type your function layout below. Line labels update down the left column automatically.")

# Clean template code structure
default_code = """def caesar_shift3(message):
    table = str.maketrans("abcdefghijklmnopqrstuvwxyz", "DEFGHIJKLMNOPQRSTUVWXYZABC")
    return message.translate(table)
"""

# Establish global track state
if "code_text" not in st.session_state:
    st.session_state.code_text = default_code
if "exec_env" not in st.session_state:
    st.session_state.exec_env = {}
if "detected_functions" not in st.session_state:
    st.session_state.detected_functions = []

# --- MULTI-COLUMN DESIGN FOR LINE NUMBERS ---
# col_nums provides a thin left margin for the numbers, col_input holds the text box
col_nums, col_input, col_testing = st.columns([1, 12, 12])

with col_nums:
    st.markdown("<br><br>", unsafe_allowed_html=True)  # Align numbers downward with text area header
    
    # Calculate how many total lines are currently typed in the state
    total_lines = len(st.session_state.code_text.split('\n'))
    
    # Format the line numbers vertically
    numbers_html = "".join([f"<div style='line-height: 25px; color: #888; font-family: monospace; text-align: right; padding-right: 5px;'>{i}</div>" for i in range(1, max(total_lines + 1, 10))])
    st.markdown(numbers_html, unsafe_allowed_html=True)

with col_input:
    with st.form(key="code_form"):
        # The text input text area
        user_code = st.text_area(
            label="Your Python Script:",
            value=st.session_state.code_text,
            height=300,
            key="sandbox_editor"
        )
        submit_button = st.form_submit_button(label="🚀 Activate My Function")
        
        # Save modifications dynamically to recalculate numbers if lines change
        if user_code != st.session_state.code_text:
            st.session_state.code_text = user_code

with col_testing:
    st.subheader("Live Output Testing")
    
    if submit_button:
        output_buffer = io.StringIO()
        sys.stdout = output_buffer
        current_env = {}
        
        try:
            # Safely evaluate script blocks
            exec(user_code, current_env)
            
            # Extract valid user functions
            found_funcs = [
                name for name, obj in current_env.items() 
                if inspect.isfunction(obj) and not name.startswith('__')
            ]
            
            sys.stdout = sys.__stdout__
            
            # Push variables into long term context states
            st.session_state.exec_env = current_env
            st.session_state.detected_functions = found_funcs
            
        except Exception as e:
            sys.stdout = sys.__stdout__
            st.error("❌ Python Execution Error:")
            st.code(traceback.format_exc(), language="python")

    # --- LIVE TESTING INTERACTION ZONE ---
    if st.session_state.detected_functions:
        target_func_name = st.session_state.detected_functions[0]
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
        st.caption("Awaiting a valid function blueprint execution layout...")
