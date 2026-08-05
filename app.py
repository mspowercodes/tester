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
st.markdown("Define your encryption function below. Line numbers are rendered down the left margin.")

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

# Main split for the interface
col_left_panel, col_right_panel = st.columns(2)

with col_left_panel:
    st.subheader("Input Python Script")
    
    # --- CRASH-PROOF LINE NUMBER MARGIN ---
    # This generates a stationary vertical column of numbers 1 to 15 
    numbers_html = ""
    for i in range(1, 16):
        numbers_html += f"<div>{i}</div>"
        
    # Injecting a styled sidebar margin that sits comfortably next to the text box
    st.markdown(
        f"""
        <div style="display: flex; margin-bottom: -45px;">
            <div style="
                font-family: monospace; 
                font-size: 14px; 
                line-height: 23px; 
                color: #888; 
                text-align: right; 
                padding-right: 10px; 
                border-right: 2px solid #444; 
                margin-top: 48px;
                height: 350px;
                user-select: none;
                min-width: 25px;
            ">
                {numbers_html}
            </div>
            <div style="flex-grow: 1; padding-left: 10px;">
                <!-- This empty container forces the flexbox space to remain aligned -->
            </div>
        </div>
        """, 
        unsafe_allowed_html=True
    )
    
    # Standard input form (completely detached from layout constraints to prevent errors)
    with st.form(key="code_form"):
        user_code = st.text_area(
            label="Your Python Script:",
            value=st.session_state.code_text,
            height=350,
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
