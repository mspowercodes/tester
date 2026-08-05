import streamlit as st
import sys
import io
import traceback
import inspect

st.set_page_config(
    page_title="Single Box Editor Sandbox",
    page_icon="🐍",
    layout="wide"
)

st.title("🐍 Single Box Python Editor Sandbox")
st.markdown("Type code inside the single window below. Line numbers match your current code structure dynamically!")

# Default starter code template
default_code = """def caesar_shift3(message):
    table = str.maketrans("abcdefghijklmnopqrstuvwxyz", "DEFGHIJKLMNOPQRSTUVWXYZABC")
    return message.translate(table)"""

# Persistent memory states
if "user_code_string" not in st.session_state:
    st.session_state.user_code_string = default_code
if "exec_env" not in st.session_state:
    st.session_state.exec_env = {}
if "detected_functions" not in st.session_state:
    st.session_state.detected_functions = []

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📝 Integrated Code Box")
    
    # 1. AUTO-GENERATED LINE GUIDES: Calculate numbers based on text line spacing
    lines_array = st.session_state.user_code_string.split("\n")
    max_lines = max(len(lines_array), 8)  # Keep a clean baseline size
    
    # Generate a matching sidebar map line guide
    guide_lines = [f"{i:2d} |" for i in range(1, max_lines + 1)]
    guide_sidebar = "\n".join(guide_lines)
    
    # Render the editor layout side-by-side cleanly within a safe form wrapper
    with st.form(key="native_editor_form"):
        # Wrap everything in a two-column setup to enforce a single box look
        col_gutter, col_editor = st.columns([1, 15])
        
        with col_gutter:
            # Displays the line counts right inside the margins
            st.code(guide_sidebar, language="text")
            
        with col_editor:
            typed_code = st.text_area(
                label="Your Script File Code Input Gutter:",
                value=st.session_state.user_code_string,
                height=215,
                label_visibility="collapsed"  # Align directly with row index 1
            )
            
        # Unified form submission button
        submit_script_trigger = st.form_submit_button(label="🚀 Run & Compile Code Block")
        
        if submit_script_trigger:
            st.session_state.user_code_string = typed_code

with col_right:
    st.subheader("🧪 Live Output Testing")
    
    # Process script parameters directly whenever data updates
    if st.session_state.user_code_string:
        output_buffer = io.StringIO()
        sys.stdout = output_buffer
        current_env = {}
        
        try:
            exec(st.session_state.user_code_string, current_env)
            
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

    # --- LIVE TESTING INTERACTION ZONE ---
    if st.session_state.detected_functions:
        # Extract the single string function name accurately from the list object
        target_func_name = st.session_state.detected_functions[0]
        target_func = st.session_state.exec_env[target_func_name]
        
        st.success(f"🎉 Active function ready: `{target_func_name}()`")
        st.write("---")
        
        test_input = st.text_input("Enter text to pass into your function:", value="hello world")
        
        try:
            live_result = target_func(test_input)
            st.write("**Function Output:**")
            st.info(f"`{live_result}`")
        except Exception as e:
            st.error(f"Error running `{target_func_name}`: {e}")
    else:
        st.caption("Awaiting successful function build from the left panel...")
