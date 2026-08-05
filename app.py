import streamlit as st
import sys
import io
import traceback

st.set_page_config(
    page_title="Single Box Editor Sandbox",
    page_icon="🐍",
    layout="wide"
)

st.title("🐍 Single Box Python Editor Sandbox")
st.markdown("Type code inside the window below and click the run button to execute instantly!")

# Default starter code template
default_code = """def caesar_shift3(message):
    table = str.maketrans("abcdefghijklmnopqrstuvwxyz", "DEFGHIJKLMNOPQRSTUVWXYZABC")
    return message.translate(table)

text = "hello world"
shifted = caesar_shift3(text)

print(f"Original text: {text}")
print(f"Shifted output: {shifted}")
"""

# Maintain application state
if "user_code_string" not in st.session_state:
    st.session_state.user_code_string = default_code

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📝 Integrated Code Box")
    
    # Render native text area acting as code input
    code_input = st.text_area(
        label="Python Script Input Window",
        value=st.session_state.user_code_string,
        height=320,
        label_visibility="collapsed"
    )
    
    # Unified submit action controller
    run_clicked = st.button("🚀 Run & Compile Code", type="primary")
    
    if run_clicked:
        st.session_state.user_code_string = code_input

with col_right:
    st.subheader("🧪 Live Output Testing")
        
    if st.session_state.user_code_string:
        output_buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = output_buffer
        current_env = {}
        
        try:
            # Safely capture execution prints
            exec(st.session_state.user_code_string, current_env)
            
            sys.stdout = old_stdout
            printed_output = output_buffer.getvalue()
            
            st.success("🎉 Code executed successfully!")
            st.write("**Console Output (stdout):**")
            
            if printed_output.strip():
                st.code(printed_output, language="plaintext")
            else:
                st.caption("Script completed but did not print any output. Use print() to display results.")
                    
        except Exception as e:
            sys.stdout = old_stdout
            st.error("❌ Python Execution Error:")
            st.code(traceback.format_exc(), language="python")
    else:
        st.caption("Awaiting successful code submission from the left panel...")
