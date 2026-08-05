import streamlit as st
import sys
import io
import traceback

st.set_page_config(
    page_title="Single Box Editor Sandbox",
    page_icon="🐍",
    layout="wide"
)

# Inject custom CSS to convert standard text area into an elegant black IDE editor
st.markdown("""
<style>
    /* Force the wrapper background to match a true code editor */
    div[data-baseweb="textarea"] {
        background-color: #1e1e1e !important;
        border: 1px solid #444 !important;
        border-radius: 4px !important;
        padding: 5px !important;
    }
    /* Style the input text to behave like code lines */
    textarea {
        color: #ffffff !important;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🐍 Single Box Python Editor Sandbox")
st.markdown("Type your function inside the window below, click run, and test your encryption on the right side.")

# Default starter template matching your Caesar shift concept
default_code = """def caesar_shift3(message):
    table = str.maketrans("abcdefghijklmnopqrstuvwxyz", "DEFGHIJKLMNOPQRSTUVWXYZABC")
    return message.translate(table)
"""

# Maintain clean session states across browser actions
if "user_code" not in st.session_state:
    st.session_state.user_code = default_code
if "execution_success" not in st.session_state:
    st.session_state.execution_success = False

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📝 Integrated Code Box")
    
    # Render code typing block
    code_input = st.text_area(
        label="Editor Window",
        value=st.session_state.user_code,
        height=300,
        label_visibility="collapsed"
    )
    
    # Process actions without risky window redirect loops
    if st.button("🚀 Run & Compile Code", type="primary"):
        st.session_state.user_code = code_input
        st.session_state.execution_success = True

with col_right:
    st.subheader("🧪 Live Output Testing")
    
    if st.session_state.execution_success:
        output_buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = output_buffer
        current_env = {}
        
        try:
            # Safely compile the script context
            exec(st.session_state.user_code, current_env)
            sys.stdout = old_stdout
            
            # Dynamically identify the encryption function inside the user code
            callable_functions = [
                name for name, obj in current_env.items() 
                if callable(obj) and not name.startswith('__')
            ]
            
            if callable_functions:
                target_func_name = callable_functions[0]
                target_func = current_env[target_func_name]
                
                st.success(f"🎉 Active function ready: `{target_func_name}()`")
                st.write("---")
                
                # --- THE RIGHT PANEL: Generate message box and display encrypted result ---
                with st.form(key="encryption_testing_form"):
                    test_input = st.text_input("Enter text to pass into your function:", value="hello world")
                    submit_action = st.form_submit_button("Encrypt Message")
                    
                    if submit_action or test_input:
                        try:
                            # Pass user input through the function compiled live
                            live_result = target_func(test_input)
                            st.write("**Function Output:**")
                            st.info(f"`{live_result}`")
                        except Exception as run_err:
                            st.error(f"Error running `{target_func_name}`: {run_err}")
            else:
                st.warning("Code executed, but no function definition was found. Please define a function (e.g., `def my_function():`).")
                
        except Exception as e:
            sys.stdout = old_stdout
            st.error("❌ Python Execution Error:")
            st.code(traceback.format_exc(), language="python")
    else:
        st.caption("Awaiting successful function build from the left panel...")
