import streamlit as st
import sys
import io
import traceback
import ast
import inspect
from code_editor import code_editor  # 👈 Import the custom code editor component

st.set_page_config(
    page_title="Interactive Python Sandbox",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Interactive Python Function Sandbox")
st.markdown("Define your encryption function below. Line numbers and highlight styles are active!")

# Default template code
default_code = """def caesar_shift3(message):
    table = str.maketrans("abcdefghijklmnopqrstuvwxyz", "DEFGHIJKLMNOPQRSTUVWXYZABC")
    return message.translate(table)
"""

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Python Script")
    
    # 👈 Setup the editor options to enforce line numbers and python syntax
    editor_options = {
        "showLineNumbers": True,
        "wrap": True,
        "mode": "python",
        "theme": "monokai"
    }
    
    # Render the advanced line-numbered input field
    # (No form wrapper needed here; clicking the editor's built-in button triggers the compile)
    editor_response = code_editor(
        code=default_code, 
        lang="python", 
        options=editor_options,
        height=[20, 25]  # Automatically scales dynamically between 20 and 25 lines high
    )
    
    # Safely pull the user code out from the component's dictionary stream
    user_code = editor_response.get("text", default_code)

with col2:
    st.subheader("Live Output Testing")
    
    # Track the active environment using Streamlit session state
    if "exec_env" not in st.session_state:
        st.session_state.exec_env = {}
    if "detected_functions" not in st.session_state:
        st.session_state.detected_functions = []

    # Process and build code automatically whenever the text inside the editor updates/submits
    if user_code:
        output_buffer = io.StringIO()
        sys.stdout = output_buffer
        current_env = {}
        
        try:
            # Execute the code to extract functions into our current scope
            exec(user_code, current_env)
            
            # Find all custom functions defined by the user
            found_funcs = [
                name for name, obj in current_env.items() 
                if inspect.isfunction(obj) and not name.startswith('__')
            ]
            
            sys.stdout = sys.__stdout__
            
            # Save elements to session state so they persist across live text inputs
            st.session_state.exec_env = current_env
            st.session_state.detected_functions = found_funcs
            
        except Exception as e:
            sys.stdout = sys.__stdout__
            st.error("❌ Python Syntax Error on Input:")
            st.code(traceback.format_exc(), language="python")

    # --- LIVE INTERACTION ZONE ---
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
            st.success(f"`{live_result}`")
        except Exception as e:
            st.error(f"Error running `{target_func_name}`: {e}")
    else:
        st.caption("Awaiting a valid function blueprint layout in the editor...")
