import streamlit as st
import sys
import io
import traceback
import inspect

st.set_page_config(
    page_title="Integrated Python Sandbox",
    page_icon="🐍",
    layout="wide"
)

st.title("🐍 Integrated Python Editor Sandbox")
st.markdown("Type code directly into the block below. Line numbers and layout structures are handled natively!")

# Default template code
default_code = """def caesar_shift3(message):
    table = str.maketrans("abcdefghijklmnopqrstuvwxyz", "DEFGHIJKLMNOPQRSTUVWXYZABC")
    return message.translate(table)"""

# Track active state variables across runs
if "exec_env" not in st.session_state:
    st.session_state.exec_env = {}
if "detected_functions" not in st.session_state:
    st.session_state.detected_functions = []

# Gather current script data
if "current_script" not in st.session_state:
    st.session_state.current_script = default_code

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📝 Editor Window")
    
    # 1. GENERATE NATIVE EDITOR: Create a unified script block with built-in line indexing
    lines = st.session_state.current_script.split("\n")
    numbered_lines = [f"{i:2d} | {line}" for i, line in enumerate(lines, start=1)]
    editor_display_text = "\n".join(numbered_lines)
    
    # Render the un-editable reference window containing perfect line numbers
    st.markdown("**Code Gutter View:**")
    st.code(editor_display_text, language="python")
    
    # Render the clean single input area directly underneath for typing modifications
    with st.form(key="editor_form"):
        user_code = st.text_area(
            label="Type or modify your script body below:",
            value=st.session_state.current_script,
            height=200
        )
        submit_button = st.form_submit_button(label="🚀 Compile & Run Script")
        
        if submit_button:
            st.session_state.current_script = user_code

with col_right:
    st.subheader("🧪 Live Output Testing")
    
    # Automatically execute script whenever compile triggers
    if st.session_state.current_script:
        output_buffer = io.StringIO()
        sys.stdout = output_buffer
        current_env = {}
        
        try:
            exec(st.session_state.current_script, current_env)
            
            found_funcs = [
                name for name, obj in current_env.items() 
                if inspect.isfunction(obj) and not name.startswith('__')
            ]
            
            sys.stdout = sys.__stdout__
            st.session_state.exec_env = current_env
            st.session_state.detected_functions = found_funcs
            
        except Exception as e:
            sys.stdout = sys.__stdout__
            st.error("❌ Python Syntax Error:")
            st.code(traceback.format_exc(), language="python")

    # --- LIVE TESTING INTERACTION ZONE ---
    if st.session_state.detected_functions:
        target_func_name = st.session_state.detected_functions[0]
        target_func = st.session_state.exec_env[target_func_name]
        
        st.success(f"🎉 Active function: `{target_func_name}()`")
        st.write("---")
        
        test_input = st.text_input("Enter text to pass into your function:", value="hello world")
        
        try:
            live_result = target_func(test_input)
            st.write("**Function Output:**")
            st.info(f"`{live_result}`")
        except Exception as e:
            st.error(f"Error running `{target_func_name}`: {e}")
    else:
        st.caption("Awaiting a valid function blueprint layout in the editor panel...")
