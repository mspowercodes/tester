import streamlit as st
import sys
import io
import traceback
import inspect

st.set_page_config(
    page_title="Interactive Python Sandbox",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Interactive Python Function Sandbox")
st.markdown("Define your encryption function below. The app will automatically detect it and let you test it live!")

# Default template code
default_code = """def caesar_shift3(message):
    table = str.maketrans("abcdefghijklmnopqrstuvwxyz", "DEFGHIJKLMNOPQRSTUVWXYZABC")
    return message.translate(table)
"""

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input Python Script")
    with st.form(key="code_form"):
        user_code = st.text_area(
            label="Your Python Script:",
            value=default_code,
            height=350
        )
        submit_button = st.form_submit_button(label="🚀 Activate My Function")

with col2:
    st.subheader("Live Output Testing")
    
    # Track the active environment using Streamlit session state
    if "exec_env" not in st.session_state:
        st.session_state.exec_env = {}
    if "detected_functions" not in st.session_state:
        st.session_state.detected_functions = []

    if submit_button:
        output_buffer = io.StringIO()
        sys.stdout = output_buffer
        
        # New clean scope environment
        current_env = {}
        
        try:
            # Execute the user's code block to load their function definitions
            exec(user_code, current_env)
            
            # Find all custom functions defined by the user
            found_funcs = [
                name for name, obj in current_env.items() 
                if inspect.isfunction(obj) and not name.startswith('__')
            ]
            
            sys.stdout = sys.__stdout__
            
            # Save variables into session state so they persist across text entry refreshes
            st.session_state.exec_env = current_env
            st.session_state.detected_functions = found_funcs
            
        except Exception as e:
            sys.stdout = sys.__stdout__
            st.error("❌ Python Execution Error:")
            st.code(traceback.format_exc(), language="python")

    # --- LIVE INTERACTION ZONE ---
    if st.session_state.detected_functions:
        # Pick the first custom function the user created
        target_func_name = st.session_state.detected_functions[0]
        target_func = st.session_state.exec_env[target_func_name]
        
        st.success(f"🎉 Active function ready: `{target_func_name}()`")
        st.write("---")
        st.write("### 🧪 Test Your Code Live")
        
        # Provide a live interactive text input
        test_input = st.text_input("Enter text to pass into your function:", value="hello world")
        
        # Automatically run their function behind the scenes using their live text input
        try:
            live_result = target_func(test_input)
            
            st.write("**Function Output:**")
            st.success(f"`{live_result}`")
        except Exception as e:
            st.error(f"Error running `{target_func_name}`: {e}")
    else:
        st.caption("Awaiting successful function build from the left panel...")
