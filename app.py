import streamlit as st
import sys
import io
import traceback

st.set_page_config(
    page_title="Dynamic Code Sandbox",
    page_icon="🐍",
    layout="wide"
)

# Apply custom CSS to make the standard text_area look like a dark-themed code editor
st.markdown("""
<style>
    /* Style the text area container */
    div[data-baseweb="textarea"] {
        background-color: #1e1e1e !important;
        border: 1px solid #444 !important;
        border-radius: 4px !important;
    }
    /* Style the actual typing area */
    textarea {
        color: #ffffff !important;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🐍 Code Sandbox & Dynamic Message Creator")

# Default starter code template
default_code = """# Write your script here
# Example: 
# status = "success"
# print("Initialization completed.")

status = "ready"
print("System loaded.")
"""

# Maintain application execution states across refreshes
if "user_code" not in st.session_state:
    st.session_state.user_code = default_code
if "code_has_run" not in st.session_state:
    st.session_state.code_has_run = False

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📝 Integrated Code Box")
    
    # Text area styled to look like an IDE editor
    code_input = st.text_area(
        label="Editor Window",
        value=st.session_state.user_code,
        height=300,
        label_visibility="collapsed"
    )
    
    # Run button
    if st.button("🚀 Run & Compile Code", type="primary"):
        st.session_state.user_code = code_input
        st.session_state.code_has_run = True
        st.rerun()

with col_right:
    st.subheader("🧪 Live Output Testing")
    
    # Only try executing if the user has triggered a run
    if st.session_state.code_has_run:
        output_buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = output_buffer
        current_env = {}
        
        try:
            # Execute whatever script the user typed
            exec(st.session_state.user_code, current_env)
            
            # Restore output stream safely
            sys.stdout = old_stdout
            printed_output = output_buffer.getvalue()
            
            st.success("🎉 Code executed successfully!")
            
            # Show output if the script used print()
            if printed_output.strip():
                st.write("**Console Output (stdout):**")
                st.code(printed_output, language="plaintext")
            
            # --- THE TARGET REWARD: Dynamically spawn the message typing box ---
            st.write("---")
            st.subheader("📥 Generated Message Input Box")
            user_message = st.text_input("Type your message here:")
            
            if user_message:
                st.info(f"**Your sent message:** {user_message}")
                
        except Exception as e:
            # Safely catch and print mistakes without crashing the page
            sys.stdout = old_stdout
            st.error("❌ Python Execution Error:")
            st.code(traceback.format_exc(), language="python")
    else:
        st.caption("Awaiting successful code submission from the left panel...")
