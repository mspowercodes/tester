import streamlit as st
import sys
import io
import traceback
import inspect
from streamlit_ace import st_ace

st.set_page_config(
    page_title="Single Box Editor Sandbox",
    page_icon="🐍",
    layout="wide"
)

st.title("🐍 Single Box Python Editor Sandbox")
st.markdown("Type code inside the window below. Line numbers are fully integrated, and code runs instantly!")

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
    
    # THE BLACK EDITOR ENGINE: True dark-mode IDE editor with native line-number tracking
    ace_code = st_ace(
        value=st.session_state.user_code_string,
        language="python",
        theme="monokai",
        keybinding="vscode",
        font_size=14,
        tab_size=4,
        height=300,
        key="ace_editor_instance"
    )
    
    # Unified Run Button that actually sends the code over to Python
    if st.button("🚀 Run & Compile Code", type="primary"):
        st.session_state.user_code_string = ace_code

with col_right:
    st.subheader("🧪 Live Output Testing")
        
    # Process script parameters directly whenever data updates
    if st.session_state.user_code_string:
        output_buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = output_buffer
        current_env = {}
                
        try:
            exec(st.session_state.user_code_string, current_env)
                        
            found_funcs = [
                name for name, obj in current_env.items() 
                if inspect.isfunction(obj) and not name.startswith('__')
            ]
                        
            sys.stdout = old_stdout
            st.session_state.exec_env = current_env
            st.session_state.detected_functions = found_funcs
                    
        except Exception as e:
            sys.stdout = old_stdout
            st.error("❌ Python Execution Error:")
            st.code(traceback.format_exc(), language="python")

    # --- LIVE TESTING INTERACTION ZONE ---
    if st.session_state.detected_functions:
        # Grabbing the first functional string from the array safely
        target_func_name = st.session_state.detected_functions[0]
        target_func = st.session_state.exec_env[target_func_name]
                
        st.success(f"🎉 Active function ready: `{target_func_name}()`")
        st.write("---")
                
        # The editable message box opens perfectly right here
        test_input = st.text_input("Enter text to pass into your function:", value="hello world")
                
        try:
            live_result = target_func(test_input)
            st.write("**Function Output:**")
            st.info(f"`{live_result}`")
        except Exception as e:
            st.error(f"Error running `{target_func_name}`: {e}")
    else:
        st.caption("Awaiting successful function build from the left panel...")
