import streamlit as st
import sys
import io
import traceback
import inspect
from streamlit_monaco import st_monaco  # Import the official VS Code core wrapper

st.set_page_config(
    page_title="VS Code Sandbox",
    page_icon="🐍",
    layout="wide"
)

st.title("🐍 Python VS Code Editor Sandbox")
st.markdown("Type code inside the true editor interface below. Line numbers and tab indenting are fully interactive!")

# Default template code
default_code = """def caesar_shift3(message):
    table = str.maketrans("abcdefghijklmnopqrstuvwxyz", "DEFGHIJKLMNOPQRSTUVWXYZABC")
    return message.translate(table)"""

# Track active state variables
if "exec_env" not in st.session_state:
    st.session_state.exec_env = {}
if "detected_functions" not in st.session_state:
    st.session_state.detected_functions = []

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📝 Editor Window")
    
    # FIX: Removed the invalid 'theme' argument to stop the TypeError crash
    user_code = st_monaco(
        value=default_code,
        height="300px",
        language="python"
    )
    
    # Simple submit button to compile the script content
    run_button = st.button("🚀 Activate My Function")

with col_right:
    st.subheader("🧪 Live Output Testing")
    
    if run_button and user_code:
        output_buffer = io.StringIO()
        sys.stdout = output_buffer
        current_env = {}
        
        try:
            # Safely compile the script string pulled out from the editor panel
            exec(user_code, current_env)
            
            found_funcs = [
                name for name, obj in current_env.items() 
                if inspect.isfunction(obj) and not name.startswith('__')
            ]
            
            sys.stdout = sys.__stdout__
            st.session_state.exec_env = current_env
            st.session_state.detected_functions = found_funcs
            
            if found_funcs:
                st.toast("Function compiled successfully!")
                
        except Exception as e:
            sys.stdout = sys.__stdout__
            st.error("❌ Python Syntax Error inside Editor:")
            st.code(traceback.format_exc(), language="python")

    # --- LIVE TESTING INTERACTION ZONE ---
    if st.session_state.detected_functions:
        target_func_name = st.session_state.detected_functions
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
        st.caption("Awaiting a valid function definition in the editor panel...")
