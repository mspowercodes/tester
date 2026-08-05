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

st.title("🐍 Interactive Python Sandbox")
st.markdown("Type your function below. The **Editor View** below the box will keep track of your line numbers automatically!")

# Standard starter code
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
    st.subheader("📝 Code Editor")
    
    # Standard text box for clean, crash-proof typing
    user_code = st.text_area(
        label="Type your script here:",
        value=default_code,
        height=250
    )
    
    # THE LINE NUMBER FIX: Break the text apart and display a real code block with permanent line numbers
    st.write("**🗂️ Editor View (With Line Numbers):**")
    st.code(user_code, language="python", line_numbers=True)
    
    # Simple submit button to run the code
    run_button = st.button("🚀 Activate My Function")

with col_right:
    st.subheader("🧪 Live Output Testing")
    
    # Process code if they click run OR if the function is already active
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
            st.error("❌ Python Execution Error:")
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
        st.caption("Awaiting a valid function definition in the editor panel...")
