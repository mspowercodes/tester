import streamlit as st
import sys
import io
import traceback
import inspect

st.set_page_config(
    page_title="Line Number Sandbox",
    page_icon="🐍",
    layout="wide"
)

st.title("🐍 Python Native Editor Sandbox")
st.markdown("Type code inside the input block. The **Code Workspace View** tracks line numbers natively, avoiding network iframe crashes!")

# Default template code
default_code = """def caesar_shift3(message):
    table = str.maketrans("abcdefghijklmnopqrstuvwxyz", "DEFGHIJKLMNOPQRSTUVWXYZABC")
    return message.translate(table)"""

# Track active state variables across runs
if "exec_env" not in st.session_state:
    st.session_state.exec_env = {}
if "detected_functions" not in st.session_state:
    st.session_state.detected_functions = []

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📝 Script Input")
    
    # Standard text area box: 100% reliable, zero rendering lag or loading loops
    user_code = st.text_area(
        label="Type or paste your Python code here:",
        value=default_code,
        height=220
    )
    
    # THE NATIVE SOLUTION: Renders line numbers dynamically directly within the text layout window
    st.write("**🗂️ Live Workspace (With Line Numbers):**")
    st.code(user_code, language="python", line_numbers=True)
    
    run_button = st.button("🚀 Activate My Function")

with col_right:
    st.subheader("🧪 Live Output Testing")
    
    # Execute code whenever 'Run' is clicked, or keep it loaded if functions exist
    if run_button or st.session_state.detected_functions:
        output_buffer = io.StringIO()
        sys.stdout = output_buffer
        current_env = {}
        
        try:
            exec(user_code, current_env)
            
            found_funcs = [
                name for name, obj in current_env.items() 
                if inspect.isfunction(obj) and not name.startswith('__')
            ]
            
            sys.stdout = sys.__stdout__
            st.session_state.exec_env = current_env
            st.session_state.detected_functions = found_funcs
            
            if run_button and found_funcs:
                st.toast("Function activated successfully!")
                
        except Exception as e:
            sys.stdout = sys.__stdout__
            st.error("❌ Python Syntax Error:")
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
        st.caption("Awaiting a valid function blueprint layout in the editor panel...")
